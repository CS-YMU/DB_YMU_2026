import streamlit as st
import pandas as pd
from db_config import (
    create_index_if_missing,
    drop_index_if_exists,
    execute_explain,
    index_exists,
)

st.set_page_config(page_title="任务1: 索引性能对比", page_icon="⚡")

st.header("⚡ 任务1: 索引性能对比")
st.markdown("对比 `employees` 表的 `last_name` 字段在**有无索引**时的查询性能差异。")


has_lastname_index = index_exists("employees", "idx_lastname")
if has_lastname_index:
    st.info("当前已存在 `idx_lastname` 索引。若要观察无索引效果，请先点击“删除索引”。")
else:
    st.info("当前不存在 `idx_lastname` 索引，适合观察全表扫描。")

col1, col2 = st.columns(2)
with col1:
    search_name = st.text_input("查询的 last_name", "Bamford")
with col2:
    st.markdown("""
    **操作步骤：**
    1. 先执行"无索引"查询，记录执行计划
    2. 创建索引
    3. 再执行"有索引"查询，对比差异
    """)

sql_eq = "SELECT * FROM employees WHERE last_name = %s"
sql_eq_params = (search_name,)
sql_range = "SELECT * FROM employees WHERE last_name >= 'B' AND last_name < 'C'"

st.subheader("📊 步骤一：无索引时的查询分析")

if st.button("🔍 执行无索引查询的 EXPLAIN", key='no_idx'):
    result = execute_explain(sql_eq, sql_eq_params)
    if result is not None:
        df = pd.DataFrame(result)
        st.dataframe(df, use_container_width=True, hide_index=True)
        row = df.iloc[0]
        if row.get('key'):
            st.warning(f"当前查询使用了索引：type={row.get('type')}, key={row.get('key')}, rows≈{row.get('rows')}。请先删除 `idx_lastname` 后再观察无索引效果。")
        else:
            st.error(f"❌ type={row.get('type')}, key={row.get('key')}, rows≈{row.get('rows')}")
            st.markdown("→ **全表扫描**，扫描整个 employees 表（约30万行）")

st.subheader("📊 步骤二：创建索引")

col_create, col_drop = st.columns(2)
with col_create:
    if st.button("➕ 创建索引: CREATE INDEX idx_lastname ON employees(last_name)", key='create_idx', type='primary'):
        ok, status = create_index_if_missing("employees", "idx_lastname", "last_name")
        if ok and status == "created":
            st.success("✅ 索引创建成功！")
        elif ok and status == "exists":
            st.info("索引已经存在，无需重复创建。")
        else:
            st.warning("索引创建失败，请查看上方错误信息。")

with col_drop:
    if st.button("➖ 删除索引: DROP INDEX idx_lastname ON employees", key='drop_idx'):
        ok, status = drop_index_if_exists("employees", "idx_lastname")
        if ok and status == "dropped":
            st.success("✅ 索引已删除")
        elif ok and status == "missing":
            st.info("索引本来就不存在。")
        else:
            st.warning("索引删除失败，请查看上方错误信息。")

st.subheader("📊 步骤三：有索引时的查询分析")

tab1, tab2 = st.tabs(["等值查询对比", "范围查询对比"])

with tab1:
    if st.button("🔍 执行等值查询的 EXPLAIN (有索引)", key='with_idx_eq'):
        result = execute_explain(sql_eq, sql_eq_params)
        if result is not None:
            df = pd.DataFrame(result)
            st.dataframe(df, use_container_width=True, hide_index=True)
            row = df.iloc[0]
            if row.get('key'):
                st.success(f"✅ type={row.get('type')}, key={row.get('key')}, rows≈{row.get('rows')}")
                st.markdown("→ **索引扫描**，仅需扫描匹配的行数。")
            else:
                st.warning("尚未使用索引，请先创建 `idx_lastname`。")

with tab2:
    if st.button("🔍 执行范围查询的 EXPLAIN", key='range_idx'):
        result = execute_explain(sql_range)
        if result is not None:
            df = pd.DataFrame(result)
            st.dataframe(df, use_container_width=True, hide_index=True)
            row = df.iloc[0]
            st.info(f"type={row.get('type')}, key={row.get('key')}, rows≈{row.get('rows')}")
            if row.get('type') == 'range':
                st.success("✅ 范围查询也使用了索引！")
            else:
                st.warning("⚠️ 范围查询未使用索引")

st.subheader("📊 步骤四：覆盖索引演示")
st.markdown("仅查询索引字段本身，无需回表查数据行，效率最高。")

cover_sql = "SELECT last_name FROM employees WHERE last_name = %s"
cover_params = (search_name,)
if st.button("🔍 EXPLAIN: SELECT last_name FROM employees WHERE last_name = '...'", key='cover_idx'):
    result = execute_explain(cover_sql, cover_params)
    if result is not None:
        df = pd.DataFrame(result)
        st.dataframe(df, use_container_width=True, hide_index=True)
        extra = str(df.iloc[0].get('Extra', ''))
        if 'Using index' in extra:
            st.success("✅ **覆盖索引 (Using index)**：只扫描索引，不读数据行，效率最高！")
        else:
            st.info(f"Extra: {extra}")

st.divider()
st.subheader("📝 实验报告要点")
st.markdown("""
| 对比项 | 无索引 | 有索引 | 覆盖索引 |
|--------|--------|--------|----------|
| type | ALL (全表扫描) | ref/range | ref |
| key | NULL | idx_lastname | idx_lastname |
| rows | ~300000 | ~10-200 | ~10-200 |
| Extra | - | - | Using index |
| 性能 | 慢 | 快 | 最快 |
""")
