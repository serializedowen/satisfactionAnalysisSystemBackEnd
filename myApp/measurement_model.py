# 验证性因子分析

import numpy as np
import warnings
import sys
np.set_printoptions(suppress=True)



# data 样本数据
# lam 因此载荷的初始值
# step 梯度下降的步长
# max_iter 最大迭代次数
# rdd 参数估计的四舍五入精度
def matrixRound(M, decPts=4):
    # 对行循环
    for index in range(len(M)):
        # 对列循环
        for _index in range(len(M[index])):
            M[index][_index] = '{:.5f}'.format(M[index][_index])
    return M




def cfa(data, lam, step=0.01, max_iter=10000, rdd=3, tol=1e-7):
    try:
        # 结构方程模型中的测量模型，验证性因子分析参数估计
        # 下面是样本协方差矩阵
        s = np.cov(data, rowvar=False, bias=True)
        # 误差协方差矩阵初值
        var_e = np.eye(lam.shape[0])
        # 潜在变量协方差矩阵初值
        phi = np.eye(lam.shape[1])
        for i in range(max_iter):
            # 估计协方差矩阵
            sigma = np.dot(np.dot(lam, phi), lam.transpose()) + var_e
            sigma_inv = np.linalg.inv(sigma)
            omega = sigma_inv - np.dot(sigma_inv,np.dot(s, sigma_inv))
            omega_lam = np.dot(omega, lam)
            # lambda的梯度
            dlam = 2 * np.dot(omega_lam, phi)
            dlam[lam == 0] = 0
            # phi的梯度
            dphi = np.dot(lam.transpose(), omega_lam)
            dphi[range(lam.shape[1]), range(lam.shape[1])] = 0
            # var_e的梯度
            dvar_e = omega
            dvar_e[var_e == 0] = 0
            delta_lam = step * dlam
            delta_var_e = step * dvar_e
            delta_phi = step * dphi
            lam = lam - delta_lam
            var_e = var_e - delta_var_e
            phi = phi - delta_phi
            if max(np.max(np.abs(delta_lam)), np.max(np.abs(delta_phi)), np.max(np.abs(delta_var_e))) < tol:
                return np.round(lam, rdd), np.round(phi, rdd), np.round(var_e, rdd)
        warnings.warn('no coverage')
        return np.round(lam, rdd), np.round(phi, rdd), np.round(var_e, rdd)
    except Exception as e:
        # 抛出异常
        return {
            "status": False,
            "msg": str(e)
        }


# 因子载荷初始值


# 获取数据

# 标准化数据
# data = parse_data_by_min_max(init_data, 2, 5)

# np.linalg.det(init_data)
# print(data)

def measurement(basePath, lam, step,max_iter, rdd ):
    try:
        path = basePath + '.dat'
        data = np.loadtxt(path)
        _lam = np.array(lam)
        result = cfa(data, _lam, float(step), int(max_iter), int(rdd))
        if type(result) == tuple:
            lam, phi, var_e = result
            # 测量模型
            # 因子载荷
            # print('=====因子载荷=====')
            # print(lam)
            # 误差方差
            # print('=====误差方差=====')
            # print(np.diag(var_e))
            # 潜变量协方差矩阵
            # print('=====潜变量协方差矩阵=====')
            # print(phi)

            return {
                "status": True,
                "lam": lam,
                "error_var_e": np.diag(var_e),
                "phi": phi
            }
        else:
            return result
    except:
        print('-------')
        return {
            "status": False,
            "msg": ''
        }