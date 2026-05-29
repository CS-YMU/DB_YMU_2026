import streamlit as st
import pandas as pd
from db_config import clean_select_sql, execute_explain

st.set_page_config(page_title="EXPLAIN分析工具", page_icon="🔍")

st.header("🔍 EXPLAIN 分析工具")
st.markdown("输入任意 SELECT 语句，查看 MySQL 的执行计划。")


st.markdown("""
**EXPLAIN 关键字段速查：**
| 字段 | 说明 | 优化提示 |
|------|------|----------|
| `type` | 访问类型 | `ALL`=全表扫描(危险), `ref`/`range`=索引扫描, `const`=常量 |
| `key` | 实际使用的索引 | `NULL`=未使用索引 |
| `rows` | 预估扫描行数 | 越小越好 |
| `Extra` | 额外信息 | `Using filesort`/`Using temporary` 需优化 |
""")

example_queries = {
    "例1: 等值查询 (无索引)": "SELECT * FROM employees WHERE last_name = 'Bamford'",
    "例2: 范围查询": "SELECT * FROM employees WHERE emp_no BETWEEN 10001 AND 10100",
    "例3: 连接查询": "SELECT e.first_name, e.last_name, s.salary FROM employees e JOIN salaries s ON e.emp_no = s.emp_no WHERE s.to_date = '9999-01-01' LIMIT 10",
    "例4: 分组排序": "SELECT last_name, COUNT(*) FROM employees GROUP BY last_name ORDER BY COUNT(*) DESC LIMIT 10",
    "例5: 子查询": "SELECT * FROM employees WHERE emp_no = (SELECT emp_no FROM salaries WHERE salary = (SELECT MAX(salary) FROM salaries WHERE to_date = '9999-01-01') AND to_date = '9999-01-01')",
}

col1, col2 = st.columns([3, 1])
with col2:
    selected_example = st.selectbox("选择示例SQL", ["自定义"] + list(example_queries.keys()))

with col1:
    if selected_example == "自定义":
        sql_input = st.text_area("输入 SELECT 语句", "SELECT * FROM employees WHERE last_name = 'Bamford'", height=100)
    else:
        sql_input = st.text_area("输入 SELECT 语句", example_queries[selected_example], height=100)

if st.button("🔍 执行 EXPLAIN 分析", type='primary'):
    sql_to_explain = clean_select_sql(sql_input)
    if not sql_to_explain.lower().startswith(("select", "with")):
        st.error("这里只允许分析 SELECT / WITH 查询。请不要输入 INSERT、UPDATE、DELETE 或 DDL。")
        st.stop()

    result = execute_explain(sql_to_explain)
    if result is not None:
        df = pd.DataFrame(result)
        st.subheader("执行计划结果")
        st.dataframe(df, use_container_width=True, hide_index=True)

        if "EXPLAIN" in df.columns:
            st.info("当前数据库返回了树形 EXPLAIN。若看不到 type/key/rows 字段，请确认数据库支持 `EXPLAIN FORMAT=TRADITIONAL`。")
            st.stop()

        st.subheader("📋 结果解读")
        for idx, row in df.iterrows():
            with st.expander(f"表: {row.get('table', 'N/A')} 的分析"):
                type_val = row.get('type', '')
                key_val = row.get('key')
                rows_val = row.get('rows', '')
                extra_val = row.get('Extra', '')

                if type_val == 'ALL':
                    st.error(f"⚠️ **type = ALL**: 全表扫描！建议检查查询条件并添加索引。")
                elif type_val in ('index', 'range', 'ref', 'eq_ref', 'const'):
                    st.success(f"✅ **type = {type_val}**: 使用了索引访问，性能较好。")
                else:
                    st.info(f"ℹ️ **type = {type_val}**")

                if key_val is None or key_val == '':
                    st.error(f"⚠️ **key = NULL**: 没有使用索引！")
                else:
                    st.success(f"✅ **key = {key_val}**: 使用了索引。")

                if rows_val and str(rows_val).isdigit() and int(rows_val) > 100000:
                    st.warning(f"⚠️ **rows = {rows_val}**: 扫描行数较多，注意优化。")

                if extra_val:
                    if 'Using filesort' in str(extra_val):
                        st.warning(f"⚠️ **Extra** 包含 `Using filesort`: 需要额外排序，大数据量时较慢。")
                    if 'Using temporary' in str(extra_val):
                        st.warning(f"⚠️ **Extra** 包含 `Using temporary`: 使用了临时表，常见于 GROUP BY / DISTINCT。")
                    if 'Using index' in str(extra_val):
                        st.success(f"✅ **Extra** 包含 `Using index`: 覆盖索引查询，无需回表，效率最高。")
