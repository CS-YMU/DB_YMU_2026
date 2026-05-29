import pandas as pd
import streamlit as st


st.set_page_config(page_title="作业与实验训练", page_icon="📝", layout="wide")

st.header("📝 作业与实验训练")
st.markdown("把课件知识点整理成可操作的小实验，学生可以边做边形成作业答案。")


tab1, tab2, tab3, tab4 = st.tabs([
    "文件组织策略",
    "记录长度计算",
    "索引查询模拟",
    "索引维护模拟",
])

with tab1:
    st.subheader("一个对象一个文件 vs 数据库大文件")
    st.markdown("案例：学校档案室如何放资料。")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**方案 A：每门课一个文件夹**")
        st.write("表、索引等对象各自对应操作系统文件。")
        st.success("优点：直观，单个对象备份、迁移、排查更方便。")
        st.warning("缺点：文件数量多时，操作系统元数据管理和打开文件成本会上升。")
        st.caption("类似 PostgreSQL、KingbaseES 的思路。")

    with c2:
        st.markdown("**方案 B：整个学院用几个大柜子**")
        st.write("DBMS 申请一个或多个大文件，内部自己管理表空间、段、块。")
        st.success("优点：空间分配灵活，减少操作系统层面的碎片和文件管理开销。")
        st.warning("缺点：内部结构复杂，损坏恢复和人工排查更依赖 DBMS 工具。")
        st.caption("类似 Oracle、SQL Server 的思路。")

    st.markdown("**课堂讨论**")
    st.info("如果数据库里有 10 万张小表，哪种方案更容易让操作系统产生压力？如果只想备份一张表，哪种方案更直观？")

with tab2:
    st.subheader("Course 表定长记录字节对齐计算")
    st.markdown("硬件喜欢按固定边界读取数据。字段如果必须从 4 或 8 的倍数字节开始，中间可能要填充空白字节。")

    default_fields = pd.DataFrame([
        {"字段": "Cno", "类型": "char(8)", "字节数": 8},
        {"字段": "Cname", "类型": "char(20)", "字节数": 20},
        {"字段": "Cpno", "类型": "char(8)", "字节数": 8},
        {"字段": "Ccredit", "类型": "int", "字节数": 4},
    ])

    st.dataframe(default_fields, use_container_width=True, hide_index=True)
    align = st.radio("字段起始位置要求", [1, 4, 8], format_func=lambda x: "任意字节" if x == 1 else f"{x} 的倍数字节", horizontal=True)

    offset = 0
    rows = []
    for _, field in default_fields.iterrows():
        padding = 0
        if align > 1 and offset % align != 0:
            padding = align - offset % align
            offset += padding
        start = offset
        offset += int(field["字节数"])
        rows.append({
            "字段": field["字段"],
            "字段字节": int(field["字节数"]),
            "前置填充": padding,
            "起始偏移": start,
            "结束偏移": offset - 1,
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.metric("一条记录总字节数", offset)
    st.info("作业答题时要写清：先列字段长度，再按对齐规则逐字段计算填充字节，最后求总长度。")

with tab3:
    st.subheader("用不同索引查询 Student 表")
    st.markdown("选择查询条件，观察不同索引结构的访问路径。")

    query = st.selectbox("查询", [
        "Sno = 20180013",
        "Sno = 20180014",
        "Sno = 20180016",
        "Sno >= 20180009",
    ])

    lookup_text = {
        "稠密索引": {
            "等值": "在索引文件中直接找到 key，再根据指针访问记录。若 key 不存在，查索引即可判定不存在。",
            "范围": "找到范围起点后，按索引顺序继续扫描后续索引项，再访问对应记录。",
        },
        "稀疏索引": {
            "等值": "先用块首索引定位到可能的数据块，再在块内顺序查找。",
            "范围": "先定位范围起点所在块，再从该块开始顺序读后续块。",
        },
        "多级索引": {
            "等值": "从最高层索引逐层向下，最后定位到一级索引或数据块。",
            "范围": "先逐层定位起点，再在底层顺序扫描。",
        },
        "B+树索引": {
            "等值": "从根结点到叶结点，所有查询路径长度接近一致。",
            "范围": "先找到起始 key 所在叶子，再沿叶子链表向右扫描。",
        },
        "哈希索引": {
            "等值": "计算 h(key) 定位桶，在桶和溢出链中查找。",
            "范围": "不适合范围查询，因为哈希桶不保持 key 的大小顺序。",
        },
    }

    mode = "范围" if ">=" in query else "等值"
    rows = [{"索引": name, "访问过程": text[mode]} for name, text in lookup_text.items()]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if query == "Sno = 20180016":
        st.warning("如果 Student 表目前最大到 20180015，那么各索引都应得出“不存在”。注意：不存在也要通过索引查找路径确认。")

with tab4:
    st.subheader("插入、删除、修改时索引如何维护")
    operation = st.selectbox("选择操作", [
        "插入 (20180016, 张婧宁, 女, 2002-1-2, 信息安全)",
        "删除 Sno = 20180004",
        "删除 Sno = 20180005",
        "修改 20180008 的专业为 计算机科学与技术",
    ])

    maintenance = [
        {
            "索引类型": "稠密索引",
            "维护要点": "插入/删除每条记录都要同步插入/删除索引项；若修改的是索引字段，要删除旧索引项并插入新索引项。",
        },
        {
            "索引类型": "稀疏索引",
            "维护要点": "只有影响块首记录或块分裂/合并时才需要改索引；普通块内记录变化可能不改索引。",
        },
        {
            "索引类型": "多级索引",
            "维护要点": "先维护底层索引；如果底层索引块变化，再逐层向上维护。",
        },
        {
            "索引类型": "辅助索引",
            "维护要点": "非排序字段变化时要维护对应指针桶。例如专业从信息管理改为计算机科学，要把记录指针从旧桶移到新桶。",
        },
        {
            "索引类型": "B+树索引",
            "维护要点": "插入可能导致叶子分裂；删除可能导致借位或合并；修改索引键通常等价于先删后插。",
        },
        {
            "索引类型": "哈希索引",
            "维护要点": "用哈希函数定位桶；插入时桶满要挂溢出桶；删除后可尝试整理溢出链。",
        },
    ]
    st.dataframe(pd.DataFrame(maintenance), use_container_width=True, hide_index=True)

    if "专业" in operation:
        st.info("本操作不改变学号索引，但会影响建立在 `Smajor` 上的辅助索引或位图索引。")
    elif "插入" in operation:
        st.info("插入新学号会影响所有以学号为 key 的索引；如果插入到有序文件中，还可能引起数据块移动或分裂。")
    else:
        st.info("删除记录时，索引项不能留下悬空指针，否则后续查询会指向已经不存在的记录。")

st.divider()
st.subheader("提交建议")
st.markdown("""
作业答案建议按“概念解释 → 例子 → 优缺点/过程”组织。实验报告建议每个任务都保留：

1. 执行的 SQL。
2. EXPLAIN 截图或关键字段：`type`、`key`、`key_len`、`rows`、`Extra`。
3. 对比结论：有没有使用索引，为什么。
""")
