import streamlit as st
import pandas as pd
from db_config import execute_explain, execute_script, table_exists

st.set_page_config(page_title="任务2: 最左前缀法则", page_icon="🔑")

st.header("🔑 任务2: 联合索引的最左前缀法则与失效场景")
st.markdown("用一个专门的演示表验证联合索引 `(emp_no, dept_no)` 的使用规则。")


st.warning("""
`employees` 示例库里的 `dept_emp` 表本身还有单列索引 `dept_no`。如果直接用它演示“跳过最左列”，
MySQL 可能会使用 `dept_no` 这个独立索引，结果会和课件预期不一致。

本页会创建一个轻量演示表 `idx_prefix_demo`：只保留主键 `(emp_no, dept_no)`，不创建单列 `dept_no` 索引。
""")

setup_sql = """
DROP TABLE IF EXISTS idx_prefix_demo;
CREATE TABLE idx_prefix_demo (
    emp_no INT NOT NULL,
    dept_no CHAR(4) NOT NULL,
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    PRIMARY KEY (emp_no, dept_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO idx_prefix_demo
SELECT emp_no, dept_no, from_date, to_date
FROM dept_emp
LIMIT 50000;

DROP TABLE IF EXISTS idx_type_demo;
CREATE TABLE idx_type_demo (
    code VARCHAR(8) NOT NULL,
    student_name VARCHAR(20) NOT NULL,
    PRIMARY KEY (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO idx_type_demo VALUES
('10001','李明'),('10002','王芳'),('10003','赵强'),('20001','刘敏'),('30001','陈晨');
""".strip()

with st.expander("准备演示表 idx_prefix_demo", expanded=True):
    st.code(setup_sql, language="sql")
    if st.button("创建/重置演示表", type="primary"):
        if execute_script(setup_sql):
            st.success("演示表已准备好。")

st.info("演示表只有一个联合主键索引，顺序是 `(emp_no, dept_no)`。可以把它想成电话簿先按姓排序，再按名排序。只知道名，很难直接查。")


def ensure_demo_table():
    if table_exists("idx_prefix_demo") and table_exists("idx_type_demo"):
        return True
    st.info("未检测到演示表，正在自动创建。")
    return execute_script(setup_sql)

st.subheader("📖 第一部分：验证最左前缀法则")

scenarios_part1 = [
    {
        "name": "1️⃣ 完整匹配索引两列",
        "sql": "SELECT * FROM idx_prefix_demo WHERE emp_no = 10001 AND dept_no = 'd005'",
        "expected": "索引完全使用（key=PRIMARY，key_len较大）",
        "badge": "✅",
        "color": "success"
    },
    {
        "name": "2️⃣ 只匹配索引最左列",
        "sql": "SELECT * FROM idx_prefix_demo WHERE emp_no = 10001",
        "expected": "使用主键索引，但 key_len 较短（只用第一列）",
        "badge": "✅",
        "color": "success"
    },
    {
        "name": "3️⃣ 跳过最左列（索引失效）",
        "sql": "SELECT * FROM idx_prefix_demo WHERE dept_no = 'd005'",
        "expected": "type=ALL（全表扫描），key=NULL，索引失效！",
        "badge": "❌",
        "color": "error"
    },
    {
        "name": "4️⃣ 验证优化器自动调整顺序",
        "sql": "SELECT * FROM idx_prefix_demo WHERE dept_no = 'd005' AND emp_no = 10001",
        "expected": "与写法一执行计划一致，优化器自动调整条件顺序",
        "badge": "✅",
        "color": "success"
    },
]

for s in scenarios_part1:
    with st.expander(f"{s['badge']} {s['name']}"):
        st.code(s['sql'], language='sql')
        st.markdown(f"**预期效果:** {s['expected']}")
        if st.button("🔍 执行 EXPLAIN", key=f"p1_{s['name']}"):
            if not ensure_demo_table():
                st.stop()
            result = execute_explain(s['sql'])
            if result is not None:
                df = pd.DataFrame(result)
                st.dataframe(df, use_container_width=True, hide_index=True)
                row = df.iloc[0]
                key_val = row.get('key')
                type_val = row.get('type')
                key_len = row.get('key_len')

                if s['color'] == 'success':
                    st.success(f"✅ key={key_val}, type={type_val}, key_len={key_len}")
                else:
                    st.error(f"❌ key={key_val}, type={type_val} → 全表扫描！")

st.subheader("📖 第二部分：索引失效场景演示")

scenarios_part2 = [
    {
        "name": "① 联合索引中范围查询后的列失效",
        "sql": "SELECT * FROM idx_prefix_demo WHERE emp_no > 10001 AND dept_no = 'd005'",
        "explain": "`emp_no > 10001` 是范围查询，其后的 `dept_no` 条件无法使用索引",
        "badge": "⚠️",
    },
    {
        "name": "② 隐式类型转换导致索引失效",
        "wrong_sql": "SELECT * FROM idx_type_demo WHERE code = 10001",
        "correct_sql": "SELECT * FROM idx_type_demo WHERE code = '10001'",
        "explain": "`code` 是字符串主键。用数值比较时，MySQL 可能把列转换成数字再比较，导致不能按字符串索引直接定位",
        "badge": "⚠️",
    },
    {
        "name": "③ LIKE 模糊查询前缀不固定",
        "wrong_sql": "SELECT * FROM idx_prefix_demo WHERE dept_no LIKE '%d00%'",
        "correct_sql": "SELECT * FROM idx_prefix_demo WHERE emp_no = 10001 AND dept_no LIKE 'd00%'",
        "explain": "前导 `%` 没有固定起点，B+树无法从左到右定位；保留最左列且前缀固定时更容易利用索引",
        "badge": "⚠️",
    },
    {
        "name": "④ 使用 OR 连接条件",
        "sql": "SELECT * FROM idx_prefix_demo WHERE emp_no = 10001 OR dept_no = 'd005'",
        "explain": "OR 条件导致索引无法有效使用（除非两边都有独立索引）",
        "badge": "⚠️",
    },
]

for s in scenarios_part2:
    with st.expander(f"{s['badge']} {s['name']}"):
        st.markdown(f"**原理:** {s['explain']}")

        if 'wrong_sql' in s and 'correct_sql' in s:
            col_w, col_c = st.columns(2)
            with col_w:
                st.markdown("❌ **错误写法**")
                st.code(s['wrong_sql'], language='sql')
                if st.button("🔍 执行错误写法", key=f"p2w_{s['name']}"):
                    if not ensure_demo_table():
                        st.stop()
                    result = execute_explain(s['wrong_sql'])
                    if result is not None:
                        df = pd.DataFrame(result)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        if df.iloc[0].get('key') is None or df.iloc[0].get('key') == '':
                            st.error("❌ 未使用索引！")
                        else:
                            st.info(f"key={df.iloc[0].get('key')}")

            with col_c:
                st.markdown("✅ **正确写法**")
                st.code(s['correct_sql'], language='sql')
                if st.button("🔍 执行正确写法", key=f"p2c_{s['name']}"):
                    if not ensure_demo_table():
                        st.stop()
                    result = execute_explain(s['correct_sql'])
                    if result is not None:
                        df = pd.DataFrame(result)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        if df.iloc[0].get('key') is not None and df.iloc[0].get('key') != '':
                            st.success("✅ 使用了索引！")
                        else:
                            st.warning("未使用索引")
        else:
            st.code(s['sql'], language='sql')
            if st.button("🔍 执行 EXPLAIN", key=f"p2_{s['name']}"):
                if not ensure_demo_table():
                    st.stop()
                result = execute_explain(s['sql'])
                if result is not None:
                    df = pd.DataFrame(result)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    type_val = df.iloc[0].get('type')
                    if type_val == 'ALL':
                        st.error("❌ 全表扫描！索引失效")
                    elif type_val == 'range':
                        st.warning(f"⚠️ type=range，注意范围查询后列是否失效")
                    else:
                        st.info(f"type={type_val}")

st.divider()
st.subheader("📝 实验报告总结")
st.markdown("""
**最左前缀法则核心：**
- 联合索引 `(a, b, c)` 必须按从左到右的顺序使用
- 查询条件必须从最左列开始，不能跳过中间列
- 遇到范围查询（`>`, `<`, `BETWEEN`, `LIKE 'xxx%'`）后，其右侧列不再使用索引

**常见索引失效场景：**
1. 违反最左前缀法则
2. 范围查询后的列
3. 隐式类型转换
4. LIKE 前导模糊匹配 (`%xxx`)
5. OR 条件连接
6. 对索引列使用函数或运算
""")
