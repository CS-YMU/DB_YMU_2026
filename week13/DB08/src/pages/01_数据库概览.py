import streamlit as st
import pandas as pd
from db_config import get_table_stats, get_table_info, get_indexes, execute_query

st.set_page_config(page_title="数据库概览", page_icon="📊")

st.header("📊 数据库概览")
st.markdown("查看 employees 数据库的表结构、索引信息和数据量统计。")


tab1, tab2, tab3 = st.tabs(["📋 表统计", "🔍 表结构", "📈 索引信息"])

with tab1:
    st.subheader("表数据量与存储统计")
    stats = get_table_stats()
    if stats:
        df = pd.DataFrame(stats)
        st.dataframe(df, use_container_width=True, hide_index=True)

        data_size = pd.to_numeric(df['DATA_SIZE_MB'], errors='coerce').fillna(0)
        index_size = pd.to_numeric(df['INDEX_SIZE_MB'], errors='coerce').fillna(0)
        table_rows = pd.to_numeric(df['TABLE_ROWS'], errors='coerce').fillna(0)

        total_data = data_size.sum()
        total_index = index_size.sum()
        total_rows = int(table_rows.sum())

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("总表数", len(df))
        c2.metric("总记录数", f"{total_rows:,}")
        c3.metric("数据空间", f"{total_data:.2f} MB")
        c4.metric("索引空间", f"{total_index:.2f} MB")
    else:
        st.error("无法获取表统计信息")

with tab2:
    st.subheader("表结构详情")
    table_names = ['employees', 'departments', 'dept_emp', 'dept_manager', 'salaries', 'titles']
    selected_table = st.selectbox("选择表", table_names)

    info = get_table_info(selected_table)
    if info:
        df = pd.DataFrame(info)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("DDL语句")
        ddl_result = execute_query(f"SHOW CREATE TABLE {selected_table}")
        if ddl_result:
            st.code(ddl_result[0].get(f'Create Table', ''), language='sql')
    else:
        st.error("无法获取表结构")

with tab3:
    st.subheader("索引信息")
    selected_idx_table = st.selectbox("选择表查看索引", table_names, key='idx_table')

    indexes = get_indexes(selected_idx_table)
    if indexes:
        df = pd.DataFrame(indexes)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.info("""
        **索引类型说明：**
        - `PRIMARY`: 主键索引（聚簇索引）
        - `UNIQUE`: 唯一索引
        - 普通索引名: 非唯一索引
        - `NON_UNIQUE=0`: 唯一索引；`NON_UNIQUE=1`: 非唯一索引
        """)
    else:
        st.error("无法获取索引信息")
