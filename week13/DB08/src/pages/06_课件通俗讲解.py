import pandas as pd
import streamlit as st


st.set_page_config(page_title="课件通俗讲解", page_icon="📚", layout="wide")

st.header("📚 DB08：关系数据库存储技术")
st.markdown("按 Markdown 课件顺序讲解。每个知识点都尽量用生活例子解释，再给学生一个能动手观察的小任务。")


with st.expander("一、为什么数据库需要存储技术？", expanded=True):
    st.markdown("淘宝店每天有下单、查询、改地址、退款。数据如果乱放，查询订单就像在一堆快递单里翻纸。")
    st.dataframe(pd.DataFrame([
        {"操作": "用户下单", "频率": "1000次", "存储挑战": "写入要快"},
        {"操作": "查询订单", "频率": "5000次", "存储挑战": "查找要快"},
        {"操作": "修改地址", "频率": "200次", "存储挑战": "更新不能太慢"},
        {"操作": "退款", "频率": "50次", "存储挑战": "要能准确定位记录"},
    ]), use_container_width=True, hide_index=True)
    st.info("本章核心：数据怎么存、怎么查得快、读写和空间怎么平衡。")

with st.expander("二、逻辑结构 vs 物理结构"):
    st.markdown("你写 SQL 时看到的是逻辑结构；硬盘真正保存的是物理结构。")
    st.dataframe(pd.DataFrame([
        {"维度": "层次", "逻辑结构": "数据库 -> 表 -> 行 -> 列", "物理结构": "文件 -> 块 -> 记录"},
        {"维度": "例子", "逻辑结构": "SELECT * FROM Student", "物理结构": "磁盘上的二进制块"},
        {"维度": "特点", "逻辑结构": "方便人理解", "物理结构": "方便机器高效读写"},
    ]), use_container_width=True, hide_index=True)
    st.success("记忆法：人看表，机器读块。")

with st.expander("三、数据库的两种存储方式（含 MySQL）"):
    st.dataframe(pd.DataFrame([
        {"方式": "一表一文件", "代表": "PostgreSQL、KingbaseES", "比喻": "每个人住自己房子", "优点": "简单直观", "缺点": "文件多时系统压力大"},
        {"方式": "DBMS 自管理", "代表": "Oracle、SQL Server", "比喻": "整栋公寓统一管理", "优点": "灵活高效", "缺点": "恢复和排查复杂"},
        {"方式": "MySQL InnoDB", "代表": "MySQL", "比喻": "可以独栋，也可以合租", "优点": "独立表空间默认推荐", "缺点": "配置项要理解"},
    ]), use_container_width=True, hide_index=True)
    st.code("SHOW VARIABLES LIKE 'innodb_file_per_table';", language="sql")
    st.caption("学生实验：在 MySQL 中运行上面的 SQL，观察 InnoDB 当前是否是一表一文件模式。")

with st.expander("四、什么是数据块？"):
    st.markdown("数据库每次 I/O 通常不是读一行，而是读整个块。块像快递柜，一个柜格里可以放多条记录。")
    block_size = st.slider("假设一个块能放几条记录", 2, 8, 4)
    record_no = st.number_input("要查询第几条记录", min_value=1, max_value=100, value=17)
    block_no = (record_no - 1) // block_size + 1
    st.metric("需要读取的数据块", f"第 {block_no} 块")
    st.info("观察：即使只要一条记录，数据库也会把它所在的整个块读入内存。")

with st.expander("五、定长记录 vs 变长记录"):
    st.dataframe(pd.DataFrame([
        {"对比项": "存储方式", "定长记录": "固定大小，预先分配", "变长记录": "按实际长度分配"},
        {"对比项": "查找速度", "定长记录": "快，能直接算位置", "变长记录": "较慢，要看偏移量"},
        {"对比项": "空间利用", "定长记录": "可能浪费", "变长记录": "更节省"},
        {"对比项": "修改操作", "定长记录": "原地覆盖", "变长记录": "可能迁移"},
    ]), use_container_width=True, hide_index=True)
    name_len = st.slider("姓名实际长度", 2, 20, 4)
    addr_len = st.slider("地址实际长度", 10, 100, 30)
    fixed = 10 + 20 + 2 + 100
    variable = 10 + name_len + 2 + addr_len
    c1, c2 = st.columns(2)
    c1.metric("定长记录占用", f"{fixed} B")
    c2.metric("变长记录占用", f"{variable} B")

with st.expander("六、块的内部组织"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**定长记录块**")
        st.code("""
块头
记录0: 20180001|李勇|男
记录1: 20180002|刘晨|女
记录2: 已删除，可复用
记录3: 20180004|张立|男
空闲空间
""")
        st.write("插入找空位；删除做标记；修改原地覆盖。")
    with col2:
        st.markdown("**变长记录块**")
        st.code("""
块头: 偏移量表
空闲空间: 在中间
记录3: 从块尾往前放
记录2: 从块尾往前放
记录1: 从块尾往前放
""")
        st.write("插入从尾部分配；删除后可能移动记录；修改可能迁移。")

with st.expander("七、关系表的五种存储方式"):
    st.dataframe(pd.DataFrame([
        {"存储方式": "堆存储", "核心思想": "乱放", "插入": "极快", "查询": "极慢", "适用": "日志、临时数据"},
        {"存储方式": "顺序存储", "核心思想": "按 Key 排序", "插入": "慢", "查询": "范围快", "适用": "范围查询多"},
        {"存储方式": "聚簇存储", "核心思想": "关联数据放一起", "插入": "一般", "查询": "连接很快", "适用": "学生+选课这类一起查"},
        {"存储方式": "B+树存储", "核心思想": "平衡树", "插入": "一般", "查询": "通用快", "适用": "主流业务表"},
        {"存储方式": "哈希存储", "核心思想": "哈希函数定位", "插入": "快", "查询": "等值极快", "适用": "精确匹配"},
    ]), use_container_width=True, hide_index=True)
    st.success("聚簇一句话：把学生和这个学生的选课记录钉在一起放，一次 I/O 拿到。")

with st.expander("八、什么是索引？"):
    st.markdown("索引就是目录。没有索引是一页页找；有索引是先查目录，再直接去目标位置。")
    st.warning("索引有代价：占空间，插入、删除、更新时也要维护。不是越多越好。")

with st.expander("九、稠密索引 vs 稀疏索引"):
    records = st.slider("记录数", 100, 10000, 1000, step=100)
    per_block = st.slider("每块记录数", 5, 100, 20)
    dense = records
    sparse = (records + per_block - 1) // per_block
    c1, c2 = st.columns(2)
    c1.metric("稠密索引条目数", dense)
    c2.metric("稀疏索引条目数", sparse)
    st.info("稠密索引像每个人一张目录卡；稀疏索引像每个书架贴一张标签。")

with st.expander("十、B+树索引"):
    st.markdown("B+树是现代数据库主流索引。高度低、I/O 少、范围查询快、查询稳定。")
    st.code("SELECT * FROM Student WHERE Sno BETWEEN 25 AND 75;", language="sql")
    st.success("先找到 25 所在叶子节点，再沿叶子链表扫到 75。")

with st.expander("十一、哈希索引"):
    sid = st.number_input("输入学号", min_value=10000, max_value=99999, value=10086)
    buckets = st.slider("桶数量", 3, 20, 10)
    st.metric("哈希桶号", int(sid) % buckets)
    st.warning("哈希后大小关系被打乱，所以不适合范围查询和排序。")

with st.expander("十二、位图索引"):
    st.markdown("位图索引适合低基数字段，比如性别、地区、状态。")
    bitmap = pd.DataFrame([
        {"姓名": "张三", "性别=男": 1, "课程=数据库": 1},
        {"姓名": "李四", "性别=男": 0, "课程=数据库": 0},
        {"姓名": "王五", "性别=男": 1, "课程=数据库": 0},
        {"姓名": "赵六", "性别=男": 0, "课程=数据库": 1},
        {"姓名": "钱七", "性别=男": 1, "课程=数据库": 1},
    ])
    bitmap["AND结果"] = bitmap["性别=男"] & bitmap["课程=数据库"]
    st.dataframe(bitmap, use_container_width=True, hide_index=True)
    st.metric("男生且选了数据库课的人数", int(bitmap["AND结果"].sum()))

with st.expander("十三、面试/考试高频题"):
    st.markdown("""
1. B+树为什么适合数据库？高度低、I/O 少、范围查询快、所有查询路径稳定。
2. 哈希为什么不适合范围查询？哈希后顺序被打乱。
3. 位图索引适合什么字段？取值少的字段，例如性别、省份、状态。
""")

with st.expander("十四、本章总结"):
    st.markdown("""
- 数据组织：逻辑结构给人看，物理结构给机器读。
- 存储方式：堆、顺序、聚簇、B+树、哈希，各有场景。
- 索引技术：B+树通用，哈希等值快，位图统计快。
- 核心目标：减少磁盘 I/O，更快找到数据。
""")

with st.expander("十五、课后思考题"):
    st.dataframe(pd.DataFrame([
        {"题号": 1, "问题": "为什么索引不能建太多？", "难度": "2星"},
        {"题号": 2, "问题": "B+树和哈希索引有什么区别？", "难度": "3星"},
        {"题号": 3, "问题": "为什么数据库按块读取而不是按行读取？", "难度": "2星"},
        {"题号": 4, "问题": "为什么 B+树叶子节点要连成链表？", "难度": "3星"},
        {"题号": 5, "问题": "什么场景适合位图索引？", "难度": "2星"},
        {"题号": 6, "问题": "聚簇存储的优缺点是什么？", "难度": "3星"},
    ]), use_container_width=True, hide_index=True)
