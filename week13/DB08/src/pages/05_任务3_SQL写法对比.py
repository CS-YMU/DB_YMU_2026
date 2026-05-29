import streamlit as st
import pandas as pd
from db_config import execute_explain, execute_query

st.set_page_config(page_title="任务3: SQL写法对比", page_icon="📐")

st.header("📐 任务3: 不同SQL写法的执行计划对比")
st.markdown("查找**所有当前员工中薪水最高的员工**的工号、姓名、薪水。对比三种SQL写法的执行计划。")


st.info("💡 目标：查询当前在职（`to_date = '9999-01-01'`）的薪水最高的员工。")

methods = [
    {
        "title": "方法一：子查询",
        "sql": """SELECT e.emp_no, e.first_name, e.last_name, s.salary
FROM employees e
JOIN salaries s ON e.emp_no = s.emp_no
WHERE s.to_date = '9999-01-01'
  AND s.salary = (SELECT MAX(s2.salary) FROM salaries s2 WHERE s2.to_date = '9999-01-01')""",
        "desc": "使用子查询先计算最高薪水，再与主表 JOIN 匹配。"
    },
    {
        "title": "方法二：窗口函数 (MySQL 8.0+)",
        "sql": """SELECT emp_no, first_name, last_name, salary
FROM (
    SELECT e.emp_no, e.first_name, e.last_name, s.salary,
           RANK() OVER (ORDER BY s.salary DESC) AS rnk
    FROM employees e
    JOIN salaries s ON e.emp_no = s.emp_no
    WHERE s.to_date = '9999-01-01'
) t
WHERE rnk = 1""",
        "desc": "使用 RANK() 窗口函数按薪水降序排名，筛选排名第一的记录。"
    },
    {
        "title": "方法三：ORDER BY + LIMIT",
        "sql": """SELECT e.emp_no, e.first_name, e.last_name, s.salary
FROM employees e
JOIN salaries s ON e.emp_no = s.emp_no
WHERE s.to_date = '9999-01-01'
ORDER BY s.salary DESC
LIMIT 1""",
        "desc": "先按薪水降序排序，取第一条记录。最直观但不一定准确（可能有并列最高）。"
    },
]

for m in methods:
    with st.expander(m['title']):
        st.markdown(f"**思路:** {m['desc']}")
        st.code(m['sql'], language='sql')

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 EXPLAIN 分析", key=f"explain_{m['title']}"):
                result = execute_explain(m['sql'])
                if result is not None:
                    df = pd.DataFrame(result)
                    st.dataframe(df, use_container_width=True, hide_index=True)
        with col2:
            if st.button("▶️ 实际执行", key=f"run_{m['title']}"):
                result = execute_query(m['sql'])
                if result is not None:
                    df = pd.DataFrame(result)
                    if df.empty:
                        st.warning("查询执行成功，但没有返回记录。")
                    else:
                        st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()
st.subheader("📊 三种方法对比分析")

st.markdown("""
| 对比维度 | 子查询 | 窗口函数 | ORDER BY + LIMIT |
|----------|--------|----------|------------------|
| **准确性** | ✅ 准确（处理并列） | ✅ 准确（RANK=1包含并列） | ⚠️ 仅返回1条，可能漏掉并列 |
| **可读性** | 中等 | 高（语义清晰） | 最高 |
| **灵活性** | 低 | 高（可扩展 Top N） | 低 |
| **性能** | 依赖优化器 | 需扫描全表计算排名 | 可利用索引快速取Top1 |
| **MySQL版本** | 全部支持 | 8.0+ | 全部支持 |

**关键观察点：**
1. **子查询**的执行计划中，注意观察是否有 `DEPENDENT SUBQUERY` 或 `MATERIALIZED`
2. **窗口函数**通常会产生派生表（`DERIVED`），可能在内存中排序
3. **ORDER BY + LIMIT** 如果 `salary` 有索引，可能只需扫描极少量行
""")

st.subheader("🎯 额外思考题")
st.markdown("""
如果给 `salaries(salary)` 添加索引，三种写法的性能会有什么变化？
尝试修改SQL，用 `DENSE_RANK()` 代替 `RANK()`，结果有何不同？
""")
