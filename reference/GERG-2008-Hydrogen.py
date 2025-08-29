import CoolProp.CoolProp as CP

def calculate_compression_factor(components, T, P_kPa):
    """
    使用GERG-2008方程计算天然气混合物的压缩因子。
    
    参数:
    components: dict, 组分名称（标准名称）和摩尔分数的字典
    T: float, 温度（单位：K）
    P_kPa: float, 压力（单位：kPa）
    
    返回:
    Z: float, 压缩因子
    """
    # 将kPa转换为Pa（CoolProp需要Pa作为单位）
    P_Pa = P_kPa * 1000.0
    
    # 构建组分列表和摩尔分数列表
    fluid_names = list(components.keys())
    fractions = list(components.values())
    
    # 使用GERG-2008混合规则的正确方式
    # 创建混合物的抽象状态对象，使用HEOS后端
    mixture = CP.AbstractState("HEOS", "&".join(fluid_names))
    
    # 设置摩尔分数
    mixture.set_mole_fractions(fractions)
    
    # 对于GERG-2008混合规则，CoolProp通常会自动应用
    # 不需要显式设置混合规则，因为HEOS后端会自动处理
    
    # 设置温度和压力
    mixture.update(CP.PT_INPUTS, P_Pa, T)
    
    # 获取压缩因子
    Z = mixture.compressibility_factor()
    return Z

def get_user_input():
    """
    获取用户输入的天然气组分信息（不包括氢气）
    """
    components = {}
    print("请输入天然气基础组分信息（输入完成后输入'done'）：")
    print("可用组分示例: Methane, Nitrogen, CarbonDioxide, Ethane, Propane, Water, HydrogenSulfide, CarbonMonoxide, Oxygen, Isobutane, Butane, Isopentane, Pentane, Hexane, Heptane, Octane, Nonane, Decane, Helium, Argon")
    print("注意: 请使用CoolProp标准名称，如Methane而不是methane")
    
    while True:
        comp_name = input("请输入组分名称: ").strip()
        if comp_name.lower() == 'done':
            break
        if comp_name.lower() == 'hydrogen':
            print("提示: 氢气将在后续单独输入，请勿在此处输入")
            continue
        
        try:
            comp_fraction = float(input(f"请输入{comp_name}的摩尔分数 (0-1): "))
            if comp_fraction < 0 or comp_fraction > 1:
                print("错误: 摩尔分数必须在0到1之间")
                continue
            components[comp_name] = comp_fraction
        except ValueError:
            print("错误: 请输入有效的数字")
    
    return components

def get_hydrogen_input():
    """
    单独获取氢气组分信息
    """
    hydrogen_fraction = 0.0
    try:
        add_hydrogen = input("是否添加氢气? (y/n): ").strip().lower()
        if add_hydrogen == 'y':
            hydrogen_fraction = float(input("请输入氢气的摩尔分数 (0-1): "))
            if hydrogen_fraction < 0 or hydrogen_fraction > 1:
                print("错误: 摩尔分数必须在0到1之间")
                return 0.0
    except ValueError:
        print("错误: 请输入有效的数字")
        return 0.0
    
    return hydrogen_fraction

def adjust_compositions_with_hydrogen(base_components, hydrogen_fraction):
    """
    调整组分比例以包含氢气
    """
    if hydrogen_fraction <= 0:
        return base_components
    
    # 计算基础组分的总和
    base_total = sum(base_components.values())
    
    # 如果基础组分总和为0，则全部为氢气
    if base_total == 0:
        return {'Hydrogen': hydrogen_fraction}
    
    # 调整基础组分的比例
    scale_factor = (1.0 - hydrogen_fraction) / base_total
    adjusted_components = {}
    
    for comp, frac in base_components.items():
        adjusted_components[comp] = frac * scale_factor
    
    # 添加氢气
    adjusted_components['Hydrogen'] = hydrogen_fraction
    
    return adjusted_components

# 示例使用
if __name__ == "__main__":
    # 获取基础组分（不包括氢气）
    base_components = get_user_input()
    
    # 单独获取氢气信息
    hydrogen_fraction = get_hydrogen_input()
    
    # 调整组分比例以包含氢气
    final_components = adjust_compositions_with_hydrogen(base_components, hydrogen_fraction)
    
    # 获取温度和压力
    try:
        T = float(input("请输入温度 (K): "))
        P_kPa = float(input("请输入压力 (kPa): "))
    except ValueError:
        print("错误: 请输入有效的数字")
        exit(1)
    
    # 计算压缩因子
    try:
        Z = calculate_compression_factor(final_components, T, P_kPa)
        print(f"\n最终组分比例:")
        for comp, frac in final_components.items():
            print(f"  {comp}: {frac:.6f}")
        print(f"压缩因子 Z: {Z:.6f}")
    except Exception as e:
        print(f"计算错误: {e}")
        print("请检查输入的组分名称是否正确（使用CoolProp标准名称）")
