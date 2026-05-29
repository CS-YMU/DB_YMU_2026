import streamlit as st
import db_config

st.set_page_config(
    page_title="DB08: 数据库存储技术与索引优化",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    margin-bottom: 0.5rem;
}
.sub-header {
    font-size: 1.1rem;
    color: #666;
    margin-bottom: 2rem;
}
.info-box {
    background-color: #f0f8ff;
    border-left: 4px solid #1f77b4;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 4px;
}
.warning-box {
    background-color: #fff8e1;
    border-left: 4px solid #ff9800;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🗄️ DB08: 数据库存储技术与索引优化</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">基于 MySQL employees 示例数据库的交互式教学演示程序</p>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ 数据库连接")

    from config import DB_CONFIG
    st.code(f"""
主机: {DB_CONFIG['host']}
用户: {DB_CONFIG['user']}
数据库: {DB_CONFIG['database']}
端口: {DB_CONFIG['port']}
    """.strip())

    if st.button("🔗 测试连接", type='primary', use_container_width=True):
        success, error = db_config.test_connection()
        if success:
            st.success("✅ 连接成功！")
        else:
            st.error(f"❌ 连接失败: {error}")

    with st.expander("修改配置"):
        st.info("编辑 config.py 修改连接信息")
        st.code("""
DB_CONFIG = {
    'host': 'localhost',
    'user': 'dylan',
    'password': '<通过 DB_PASSWORD 环境变量设置>',
    'database': 'employees',
    ...
}
        """.strip())

    st.divider()
    st.markdown("""
    **📚 本周内容**
    - 8.1 数据组织
    - 8.2 索引技术
    - 作业08: 存储技术理论
    - 实验08: MySQL索引优化
    """)

st.markdown("""
<div class="info-box">
<h3>📖 程序说明</h3>
<p>本程序严格围绕 <code>DB08_MD_课件.md</code> 的章节顺序开发，用通俗案例、p5.js 动画和 MySQL 可执行实验帮助学生理解：</p>
<ul>
<li><b>为什么需要存储技术</b> — 淘宝店订单越来越慢的问题</li>
<li><b>逻辑结构 vs 物理结构</b> — 人看表，机器读块</li>
<li><b>MySQL InnoDB 存储方式</b> — 独立表空间与共享表空间</li>
<li><b>数据块、定长/变长记录、块内组织</b> — 快递柜、宿舍床位、行李箱类比</li>
<li><b>五种表组织方式</b> — 堆、顺序、聚簇、B+树、哈希</li>
<li><b>索引机制</b> — B+树、哈希、位图索引</li>
<li><b>p5.js 动画案例</b> — 按块读取、B+树范围扫描、哈希冲突、位图 AND</li>
<li><b>EXPLAIN 分析</b> — 查询执行计划的可视化解读</li>
</ul>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 实验任务导航")
    st.markdown("""
    | 页面 | 内容 | 对应实验 |
    |------|------|----------|
    | **数据库概览** | 表结构、索引、数据量统计 | 实验准备 |
    | **EXPLAIN分析工具** | 自由输入SQL查看执行计划 | 实验准备二 |
    | **任务1: 索引性能对比** | 有无索引的查询性能差异 | 任务1 (40分) |
    | **任务2: 最左前缀法则** | 联合索引验证与失效场景 | 任务2 (30分) |
    | **任务3: SQL写法对比** | 子查询/窗口函数/LIMIT对比 | 任务3 (30分) |
    | **课件通俗讲解** | 按 Markdown 课件 15 节讲解 | 课件理论 |
    | **索引结构互动演示** | 顺序/辅助/B+树/哈希/位图索引 | 课件理论 |
    | **作业与实验训练** | 作业题拆解与索引维护模拟 | 作业08 |
    | **p5动画案例** | 块读取/B+树/哈希/位图动画 | 课堂演示 |
    """)

with col2:
    st.subheader("⚡ 快速开始")
    st.markdown("""
    <div class="warning-box">
    <b>第一步：</b>在左侧配置并测试MySQL连接<br>
    <b>第二步：</b>确保已导入 employees.sql：<br>
    <code>mysql -u root -p &lt; employees.sql</code><br>
    <b>第三步：</b>从左侧导航栏选择页面开始探索
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📊 employees数据库表结构")
    st.markdown("""
    ```
    employees      (30万员工信息)
    departments    (9个部门)
    dept_emp       (员工-部门关系)
    dept_manager   (部门经理)
    salaries       (薪资记录)
    titles         (职位记录)
    ```
    """)

st.divider()
st.caption("云南民族大学 数学与计算机科学学院 | 数据库系统课程 © 2025")
