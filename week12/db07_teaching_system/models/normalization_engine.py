"""
DB07 规范化理论核心计算引擎

所有算法均返回带步骤追踪的结果，方便前端分步展示教学过程。

FD 格式约定:
    输入: [["A", "B"], ["B", "C"]]  表示 {A→B, B→C}
    内部: [("A", "B"), ("B", "C")]
"""

from itertools import combinations


def _to_tuples(fds):
    """将输入 FD 列表统一转为 (left, right) 元组"""
    return [(str(fd[0]), str(fd[1])) for fd in fds]


def _all_attrs(fds):
    """从 FD 集中提取所有出现的属性"""
    attrs = set()
    for left, right in fds:
        attrs.update(left)
        attrs.update(right)
    return attrs


def compute_closure(x, fds, given_attrs=None):
    """
    计算属性集 X 的闭包 X⁺，返回每一步推导。

    返回:
        {
            "closure": ["A","B","C"],
            "closure_str": "{A, B, C}",
            "is_superkey": True/False,
            "steps": [{"trigger": "A→B", "added": "B", "closure_after": "{A, B}"}, ...]
        }
    """
    fds = _to_tuples(fds)
    x = set(str(a) for a in x.upper().replace(" ", "").replace(",", ""))
    all_attrs_set = given_attrs or _all_attrs(fds) | x
    closure = set(x)
    steps = []
    changed = True

    while changed:
        changed = False
        for left, right in fds:
            left_set = set(left)
            right_set = set(right)
            if left_set <= closure and not right_set <= closure:
                added = right_set - closure
                closure.update(right_set)
                steps.append({
                    "trigger": f"{left}→{right}",
                    "trigger_note": f"因为 {left} ⊆ {_fmt_set(closure - right_set)}，所以加入 {right}",
                    "added": "".join(sorted(added)),
                    "closure_after": _fmt_set(closure),
                })
                changed = True

    sorted_closure = sorted(closure)
    is_superkey = all_attrs_set and all_attrs_set <= closure

    return {
        "closure": sorted_closure,
        "closure_str": _fmt_set(sorted_closure),
        "is_superkey": is_superkey,
        "superkey_note": f"X⁺ = {_fmt_set(sorted_closure)}，{'包含' if is_superkey else '不包含'}全部属性 {_fmt_set(all_attrs_set)}，{'是' if is_superkey else '不是'}超键",
        "steps": steps,
    }


def _closure_set(x, fds):
    """快速计算闭包（集合版，无步骤追踪），供其他算法内部使用"""
    closure = set(x)
    changed = True
    while changed:
        changed = False
        for left, right in fds:
            if set(left) <= closure:
                added = set(right) - closure
                if added:
                    closure.update(right)
                    changed = True
    return closure


def find_candidate_keys(attributes, fds):
    """
    求解所有候选键。

    返回:
        {
            "keys": [["A"], ["B","C"]],
            "keys_str": ["A", "BC"],
            "steps": [...]
        }
    """
    fds = _to_tuples(fds)
    all_attrs = set(str(a) for a in attributes)
    steps = []
    keys = []

    # 从单属性开始，逐步增加属性数量
    for size in range(1, len(all_attrs) + 1):
        found_at_this_size = False
        for combo in combinations(sorted(all_attrs), size):
            combo_set = set(combo)

            # 剪枝：如果组合已包含已知候选键，跳过
            if any(set(key) <= combo_set and set(key) != combo_set for key in keys):
                continue

            closure = _closure_set(combo, fds)
            is_key = closure >= all_attrs

            if is_key:
                # 检查极小性：任意真子集都不是超键
                is_minimal = True
                for r in range(1, len(combo)):
                    for sub_combo in combinations(combo, r):
                        if _closure_set(set(sub_combo), fds) >= all_attrs:
                            is_minimal = False
                            break
                    if not is_minimal:
                        break

                if is_minimal:
                    keys.append("".join(sorted(combo)))
                    steps.append({
                        "checked": "".join(sorted(combo)),
                        "closure": _fmt_set(_closure_set(combo_set, fds)),
                        "result": "候选键",
                        "note": f"({"".join(sorted(combo))})⁺ = {_fmt_set(_closure_set(combo_set, fds))} = U，且任意真子集的闭包 ≠ U",
                    })
                    found_at_this_size = True
                else:
                    steps.append({
                        "checked": "".join(sorted(combo)),
                        "closure": _fmt_set(_closure_set(combo_set, fds)),
                        "result": "超键但不极小",
                        "note": "存在真子集也是超键",
                    })
            else:
                steps.append({
                    "checked": "".join(sorted(combo)),
                    "closure": _fmt_set(_closure_set(combo_set, fds)),
                    "result": "不是超键",
                    "note": f"闭包 = {_fmt_set(_closure_set(combo_set, fds))} ≠ U",
                })

        # 如果当前大小找到了候选键，且所有更大的组合都包含已有的候选键，则可以停止
        # 实际上，如果找到了候选键，更大的组合只要包含它就会被跳过
        # 但可能有多个不互相包含的候选键（如 AB 和 AC），需要继续检查同大小和更大

    return {
        "keys": [list(k) for k in keys],
        "keys_str": keys,
        "all_attrs": sorted(all_attrs),
        "all_attrs_str": _fmt_set(all_attrs),
        "steps": steps,
    }


def compute_minimal_cover(fds):
    """
    计算最小依赖集（最小覆盖），分三步展示。

    返回:
        {
            "original": [["A","BC"], ["B","C"], ...],
            "step1": { "description": "...", "result": [["A","B"], ...], "steps": [...] },
            "step2": { "description": "...", "result": [["A","B"], ...], "steps": [...] },
            "step3": { "description": "...", "result": [["A","B"], ...], "steps": [...] },
            "minimal_cover": [["A","B"], ["B","C"]]
        }
    """
    fds = _to_tuples(fds)
    all_steps = {"original": [[l, r] for l, r in fds]}

    # Step 1: 右部单属性化
    step1_result = []
    step1_steps = []
    for left, right in fds:
        for attr in right:
            fd = (left, attr)
            if fd not in step1_result:
                step1_result.append(fd)
                step1_steps.append({
                    "action": f"分解 {left}→{right}",
                    "result": f"{left}→{attr}",
                    "note": f"将右部 {right} 拆为单属性 {attr}",
                })

    all_steps["step1"] = {
        "description": "第一步：将右部化为单属性",
        "result": [[l, r] for l, r in step1_result],
        "steps": step1_steps,
    }

    # Step 2: 消除冗余的函数依赖
    step2_result = list(step1_result)
    step2_steps = []
    for fd in step1_result:
        temp = [f for f in step2_result if f != fd]
        left = fd[0]
        right = fd[1]
        closure = _closure_set(left, temp)

        if right in closure:
            step2_steps.append({
                "action": f"检查 {left}→{right} 是否冗余",
                "detail": f"去掉 {left}→{right} 后，({left})⁺ = {_fmt_set(closure)}，包含 {right}",
                "result": "冗余，删除",
            })
            step2_result.remove(fd)
        else:
            step2_steps.append({
                "action": f"检查 {left}→{right} 是否冗余",
                "detail": f"去掉 {left}→{right} 后，({left})⁺ = {_fmt_set(closure)}，不包含 {right}",
                "result": "必需保留",
            })

    all_steps["step2"] = {
        "description": "第二步：消除冗余的函数依赖",
        "result": [[l, r] for l, r in step2_result],
        "steps": step2_steps,
    }

    # Step 3: 消除左部冗余属性
    step3_result = []
    step3_steps = []
    for left, right in step2_result:
        if len(left) == 1:
            step3_result.append((left, right))
            step3_steps.append({
                "action": f"检查 {left}→{right}",
                "detail": "左部为单属性，无需检查",
                "result": "保留",
            })
            continue

        kept_left = list(left)
        # 尝试从当前保留的左部去掉每个属性
        for attr in list(kept_left):
            test_left = "".join(a for a in kept_left if a != attr)
            if not test_left:
                continue
            closure = _closure_set(test_left, step2_result)
            if right in closure:
                step3_steps.append({
                    "action": f"检查 {left}→{right}，去掉左部属性 {attr}",
                    "detail": f"({test_left})⁺ = {_fmt_set(closure)}，仍包含 {right}",
                    "result": f"属性 {attr} 冗余，从 {left} 中去掉",
                })
                kept_left.remove(attr)
            else:
                step3_steps.append({
                    "action": f"检查 {left}→{right}，去掉左部属性 {attr}",
                    "detail": f"({test_left})⁺ = {_fmt_set(closure)}，不包含 {right}",
                    "result": f"属性 {attr} 必需保留",
                })

        new_left = "".join(sorted(kept_left))
        fd_new = (new_left, right)
        if fd_new not in step3_result:
            step3_result.append(fd_new)

    all_steps["step3"] = {
        "description": "第三步：消除左部冗余属性",
        "result": [[l, r] for l, r in step3_result],
        "steps": step3_steps,
    }

    all_steps["minimal_cover"] = [[l, r] for l, r in step3_result]

    return all_steps


def check_normal_form(attributes, fds):
    """
    判断关系模式满足的最高范式（1NF ~ BCNF），并指出违反的依赖。

    返回:
        {
            "highest_nf": "3NF",
            "is_1nf": True, "is_2nf": True, "is_3nf": True, "is_bcnf": False,
            "candidate_keys": [...],
            "prime_attrs": [...],
            "violations": [...],
            "analysis": "详细分析文字"
        }
    """
    fds = _to_tuples(fds)
    all_attrs = set(str(a) for a in attributes)

    # 先找所有的候选键
    ck_result = find_candidate_keys(attributes, fds)
    ck_list = [list(k) for k in ck_result["keys_str"]]

    # 计算主属性集合
    prime_attrs = set()
    for ck in ck_list:
        prime_attrs.update(ck)

    non_prime_attrs = all_attrs - prime_attrs

    analysis_parts = []
    violations = []

    # 1NF: 总是满足（假设属性原子化）
    is_1nf = True
    analysis_parts.append(f"1NF: 满足（假设所有属性值均为原子值）")

    # 2NF: 非主属性不能部分依赖于候选键
    is_2nf = True
    if ck_list:
        for ck in ck_list:
            ck_set = set(ck)
            for left, right in fds:
                left_set = set(left)
                # 检查 left 是否是 CK 的真子集
                if left_set < ck_set and left_set:
                    for attr in right:
                        if attr in non_prime_attrs:
                            is_2nf = False
                            violations.append({
                                "nf": "2NF",
                                "fd": f"{left}→{attr}",
                                "reason": f"非主属性 {attr} 部分依赖于候选键 {''.join(sorted(ck))}（{left} 是 {''.join(sorted(ck))} 的真子集）",
                            })

    if is_2nf:
        analysis_parts.append("2NF: 满足（所有非主属性完全函数依赖于候选键）")
    else:
        analysis_parts.append(f"2NF: 不满足（存在 {len([v for v in violations if v['nf']=='2NF'])} 个部分依赖违规）")

    # 3NF: 非主属性不能传递依赖于候选键；或等价定义：任意非平凡 FD X→A，X 是超键或 A 是主属性
    is_3nf = True
    for left, right in fds:
        left_set = set(left)
        # 跳过平凡依赖
        if set(right) <= left_set:
            continue
        # 检查 left 是否为超键
        if _closure_set(left_set, fds) < all_attrs:
            # left 不是超键，检查右部是否全是主属性
            for attr in right:
                if attr in non_prime_attrs:
                    is_3nf = False
                    violations.append({
                        "nf": "3NF",
                        "fd": f"{left}→{attr}",
                        "reason": f"左部 {left} 不是超键，且右部 {attr} 不是主属性",
                    })

    if is_3nf:
        analysis_parts.append("3NF: 满足（每个非平凡FD的左部是超键，或右部为主属性）")
    else:
        analysis_parts.append(f"3NF: 不满足（存在 {len([v for v in violations if v['nf']=='3NF'])} 个违规依赖）")

    # BCNF: 每个非平凡 FD 的左部必须是超键
    is_bcnf = True
    for left, right in fds:
        left_set = set(left)
        if set(right) <= left_set:
            continue  # 平凡依赖
        if _closure_set(left_set, fds) < all_attrs:
            is_bcnf = False
            # 避免重复记录（可能已经在3NF中记录过）
            already = any(v["fd"] == f"{left}→{right}" and v["nf"] == "BCNF" for v in violations)
            if not already:
                violations.append({
                    "nf": "BCNF",
                    "fd": f"{left}→{right}",
                    "reason": f"非平凡依赖 {left}→{right} 中，左部 {left} 不是超键",
                })

    if is_bcnf:
        analysis_parts.append("BCNF: 满足（每个非平凡FD的左部都是超键）")
    else:
        analysis_parts.append(f"BCNF: 不满足（存在不以超键为左部的非平凡依赖）")

    # 判定最高范式
    if is_bcnf:
        highest = "BCNF"
    elif is_3nf:
        highest = "3NF"
    elif is_2nf:
        highest = "2NF"
    else:
        highest = "1NF"

    return {
        "highest_nf": highest,
        "is_1nf": is_1nf,
        "is_2nf": is_2nf,
        "is_3nf": is_3nf,
        "is_bcnf": is_bcnf,
        "candidate_keys": ck_list,
        "prime_attrs": sorted(prime_attrs),
        "non_prime_attrs": sorted(non_prime_attrs),
        "violations": violations,
        "analysis": "\n".join(analysis_parts),
    }


def test_lossless_join(attributes, fds, decomposition):
    """
    使用 Chase 过程算法测试无损连接分解。

    参数:
        attributes: 所有属性列表，如 ["A","B","C","D"]
        fds: 函数依赖集
        decomposition: 分解列表，如 [["A","B"], ["B","C"], ["C","D"]]

    返回:
        {
            "is_lossless": True/False,
            "initial_table": [...],
            "steps": [...],
            "final_table": [...],
            "all_a_row_index": 0,
        }
    """
    fds = _to_tuples(fds)
    all_attrs = list(str(a) for a in attributes)
    attr_index = {a: i for i, a in enumerate(all_attrs)}
    n_attrs = len(all_attrs)
    n_subs = len(decomposition)

    # 初始化表格
    table = []
    for i, sub in enumerate(decomposition):
        row = []
        for j, attr in enumerate(all_attrs):
            if attr in sub:
                row.append(f"a{j+1}")
            else:
                row.append(f"b{i+1}{j+1}")
        table.append(row)

    initial_table = [list(row) for row in table]

    steps = []

    # Chase 过程
    changed = True
    while changed:
        changed = False
        for left, right in fds:
            left_set = set(left)
            right_set = set(right)
            left_indices = [attr_index[a] for a in left if a in attr_index]
            right_indices = [attr_index[a] for a in right if a in attr_index]

            if not left_indices:
                continue

            # 找在 left 属性上相等的行组
            for i in range(n_subs):
                for j in range(i + 1, n_subs):
                    if all(table[i][k] == table[j][k] for k in left_indices):
                        # 在 right 属性上统一值
                        for k in right_indices:
                            old_i, old_j = table[i][k], table[j][k]
                            if table[i][k] != table[j][k]:
                                # 优先保留 a 类符号
                                if table[i][k].startswith("a"):
                                    table[j][k] = table[i][k]
                                elif table[j][k].startswith("a"):
                                    table[i][k] = table[j][k]
                                else:
                                    # 都非 a，取下标较小的
                                    table[i][k] = min(table[i][k], table[j][k], key=lambda x: (x[0] != "a", x))
                                    table[j][k] = table[i][k]
                                if table[i][k] != old_i or table[j][k] != old_j:
                                    changed = True
                                    steps.append({
                                        "fd": f"{left}→{right}",
                                        "row_i": i + 1,
                                        "row_j": j + 1,
                                        "attr": all_attrs[k],
                                        "old_values": [old_i, old_j],
                                        "new_value": table[i][k],
                                        "note": f"第{i+1}行和第{j+1}行在 {left} 上相等，修改 {all_attrs[k]} 的值",
                                        "table_snapshot": [list(row) for row in table],
                                    })

    # 检查是否有全 a 行
    all_a_row = None
    for i, row in enumerate(table):
        if all(cell.startswith("a") for cell in row):
            all_a_row = i
            break

    return {
        "is_lossless": all_a_row is not None,
        "all_a_row_index": all_a_row,
        "all_attrs": all_attrs,
        "decomposition": decomposition,
        "initial_table": initial_table,
        "steps": steps,
        "final_table": table,
    }


def _fmt_set(s):
    """格式化属性集为 {A, B, C} 形式"""
    if isinstance(s, set):
        s = sorted(s)
    if not s:
        return "{}"
    return "{" + ", ".join(str(x) for x in sorted(s)) + "}"
