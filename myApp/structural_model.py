import numpy as np
import warnings
np.set_printoptions(suppress=True)

# 求样本协方差矩阵的函数


def _get_s(y, x, data):
    # 计算样本协方差矩阵
    y.extend(x)
    new_data = data[:, y]
    s = np.cov(new_data, rowvar=False, bias=True)
    return s


# 计算三种参数估计方法的 [公式] 矩阵函数
def _get_ml_omega(s, sigma):
    # 计算极大似然下的omega矩阵
    temp1 = np.linalg.inv(sigma)
    temp2 = np.dot(s, temp1)
    temp3 = temp1 - np.dot(temp1, temp2)
    return temp3


def _get_uls_omega(s, sigma):
    # 计算最小二乘法下的omega矩阵
    return sigma - s


def _get_gls_omega(s, sigma):
    # 计算广义最小二乘法下的omega矩阵
    temp = np.linalg.inv(s)
    return np.dot(np.dot(temp, sigma - s), temp)

# 计算估计协方差矩阵的函数


def _get_sigma_xx(lam_x, phi_x, var_e_x):
    # 计算估计出来的内源变量协方差矩阵
    sigma_xx = np.dot(np.dot(lam_x, phi_x), lam_x.transpose()) + var_e_x
    return sigma_xx


def _get_sigma_xy_yx(lam_x, phi_x, lam_y, gama, _beta):
    # 计算估计出来的外源变量和内源变量的协方差矩阵
    temp1 = np.dot(lam_x, phi_x)
    temp2 = np.dot(temp1, gama.transpose())
    temp3 = np.dot(temp2, _beta.transpose())
    sigma_xy = np.dot(temp3, lam_y.transpose())
    sigma_yx = sigma_xy.transpose()
    return sigma_xy, sigma_yx


def _get_sigma_yy(lam_y, _beta, gama, phi_x, var_e, var_e_y):
    # 计算估计出来的外源变量协方差矩阵
    temp1 = np.dot(lam_y, _beta)
    temp2 = np.dot(np.dot(gama, phi_x), gama.transpose()) + var_e
    temp3 = np.dot(temp1, temp2)
    sigma_yy = np.dot(temp3, temp1.transpose()) + var_e_y
    return sigma_yy


def _get_sigma(sigma_yy, sigma_yx, sigma_xy, sigma_xx):
    # 计算估计出来的协方差矩阵
    top = np.column_stack((sigma_yy, sigma_yx))
    btm = np.column_stack((sigma_xy, sigma_xx))
    return np.row_stack((top, btm))

# 验证参数精度的函数


def _check_coverage(tol=1e-7, *args):
    for arg in args:
        if np.any(np.abs(arg) > tol):
            return False
    return True

# 结构方程模型的参数估计代码


def sem(data, y, x, lam_x, lam_y, beta, gamma, method='ml', step=0.1, max_iter=50000, tol=1e-7):
    try:
        y_len = len(y)
        # 样本协方差矩阵
        s = _get_s(y, x, data)
        # 内源变量协方差矩阵
        phi_x = np.eye(lam_x.shape[1])
        # 内源变量误差协方差矩阵
        var_e_x = np.eye(lam_x.shape[0])
        # 外源变量误差协方差矩阵
        var_e_y = np.eye(lam_y.shape[0])
        # 路径方程误差协方差矩阵
        var_e = np.eye(lam_y.shape[1])
        # 依据不同的参数估计方法确定omega矩阵计算方式
        if method == 'uls':
            get_omega_method = _get_uls_omega
        elif method == 'gls':
            get_omega_method = _get_gls_omega
        else:
            get_omega_method = _get_ml_omega
        for i in range(max_iter):
            # print('------', np.eye(len(beta)) - beta)
            _beta = np.linalg.inv(np.eye(len(beta)) - beta)
            sigma_xx = _get_sigma_xx(lam_x, phi_x, var_e_x)
            sigma_yy = _get_sigma_yy(lam_y, _beta, gamma, phi_x, var_e, var_e_y)
            sigma_xy, sigma_yx = _get_sigma_xy_yx(
                lam_x, phi_x, lam_y, gamma, _beta)
            # 估计协方差矩阵
            sigma = _get_sigma(sigma_yy, sigma_yx, sigma_xy, sigma_xx)
            # 连锁求导的omega矩阵
            omega = get_omega_method(s, sigma)
            omega_xx = omega[y_len:, y_len:]
            omega_yy = omega[:y_len, :y_len]
            omega_xy = omega[y_len:, :y_len]
            omega_yx = omega[:y_len, y_len:]

            # var_e的梯度，检查
            lam_y_beta = np.dot(lam_y, _beta)
            dvar_e = np.dot(np.dot(lam_y_beta.transpose(), omega_yy), lam_y_beta)
            dvar_e[var_e == 0] = 0

            # phi_x的梯度，检查
            lam_y_beta_gama = np.dot(lam_y_beta, gamma)
            dphi_x0 = np.dot(np.dot(lam_y_beta_gama.transpose(),
                                    omega_yy), lam_y_beta_gama)
            dphi_x1 = np.dot(np.dot(lam_x.transpose(), omega_xy), lam_y_beta_gama)
            dphi_x2 = dphi_x1.transpose()
            dphi_x3 = np.dot(np.dot(lam_x.transpose(), omega_xx), lam_x)
            dphi_x = dphi_x0 + dphi_x1 + dphi_x2 + dphi_x3
            dphi_x[range(lam_x.shape[1]), range(lam_x.shape[1])] = 0

            # lam_y的梯度
            path_cov = np.dot(np.dot(gamma, phi_x), gamma.transpose()) + var_e
            beta_path_beta = np.dot(np.dot(_beta, path_cov), _beta.transpose())
            dlam_y1 = 2 * np.dot(np.dot(omega_yy, lam_y), beta_path_beta)
            dlam_y2_temp1 = np.dot(
                np.dot(np.dot(_beta, gamma), phi_x), lam_x.transpose())
            dlam_y2 = 2 * np.dot(omega_yx, dlam_y2_temp1.transpose())
            dlam_y = dlam_y1 + dlam_y2
            dlam_y[lam_y == 0] = 0

            # 固定外源变量每个潜变量的第一个因子载荷为1
            for j in range(dlam_y.shape[1]):
                _temp = dlam_y[dlam_y[:, j] != 0, j]
                _temp[0] = 0
                dlam_y[dlam_y[:, j] != 0, j] = _temp

            # lam_x的梯度
            dlam_x1 = 2 * np.dot(np.dot(omega_xx, lam_x), phi_x)
            dlam_x2_temp1 = np.dot(lam_y_beta_gama, phi_x)
            dlam_x2 = 2 * np.dot(omega_xy, dlam_x2_temp1)
            dlam_x = dlam_x1 + dlam_x2
            dlam_x[lam_x == 0] = 0

            # gama的梯度
            dgama1 = 2 * \
                np.dot(np.dot(
                    np.dot(np.dot(lam_y_beta.transpose(), omega_yy), lam_y_beta), gamma), phi_x)
            dgama2 = 2 * \
                np.dot(np.dot(np.dot(lam_y_beta.transpose(), omega_yx), lam_x), phi_x)
            dgama = dgama1 + dgama2
            dgama[gamma == 0] = 0

            # beta的梯度
            dbeta1 = 2 * np.dot(np.dot(np.dot(np.dot(lam_y_beta.transpose(),
                                                     omega_yy), lam_y_beta), path_cov), _beta)
            dbeta2_temp1 = np.dot(np.dot(lam_x, phi_x), gamma.transpose())
            dbeta2 = 2 * \
                np.dot(np.dot(np.dot(lam_y_beta.transpose(),
                                     omega_yx), dbeta2_temp1), _beta)
            dbeta = dbeta1 + dbeta2
            dbeta[beta == 0] = 0

            #  var_e_x, var_e_y的梯度
            dvar_e_y = omega_yy
            dvar_e_y[var_e_y == 0] = 0
            dvar_e_x = omega_xx
            dvar_e_x[var_e_x == 0] = 0

            # 梯度下降
            delta_var_e_x = step * dvar_e_x
            var_e_x = var_e_x - delta_var_e_x
            delta_var_e_y = step * dvar_e_y
            var_e_y = var_e_y - delta_var_e_y
            delta_var_e = step * dvar_e
            var_e = var_e - delta_var_e
            delta_phi_x = step * dphi_x
            phi_x = phi_x - delta_phi_x
            delta_lam_y = step * dlam_y
            lam_y = lam_y - delta_lam_y
            delta_lam_x = step * dlam_x
            lam_x = lam_x - delta_lam_x
            delta_gama = step * dgama
            gamma = gamma - delta_gama
            delta_beta = step * dbeta
            beta = beta - delta_beta
            if _check_coverage(tol, delta_var_e, delta_var_e_y, delta_var_e, delta_phi_x,
                               delta_lam_y, delta_lam_x, delta_gama, delta_beta):
                return np.round(lam_x, 3), np.round(lam_y, 3), np.round(phi_x, 3), np.round(beta, 3), \
                    np.round(gamma, 3), np.round(var_e, 3), np.round(
                        var_e_x, 3), np.round(var_e_y, 3)
        warnings.warn('no coverage')
        return np.round(lam_x, 3), np.round(lam_y, 3), np.round(phi_x, 3), np.round(beta, 3), \
            np.round(gamma, 3), np.round(var_e, 3), np.round(
                var_e_x, 3), np.round(var_e_y, 3)

    except Exception as e:
        return {

            "status": False,

            "msg": str(e)

        }



def structural(basePath, y, x, lam_x, lam_y, beta, gamma, method, step=0.1, max_iter=50000, tol=1e-7 ):
    try:
        path = basePath + '.dat'
        data = np.loadtxt(path)
        _lam_x = np.array(lam_x)
        _lam_y = np.array(lam_y)
        _beta = np.array(beta)
        _gamma = np.array(gamma)

        result = sem(data, y, x, _lam_x, _lam_y, _beta, _gamma, method, float(step), int(max_iter))

        if type(result) == tuple:
            lam_x, lam_y, phi_x, beta, gamma, var_e, var_e_x, var_e_y = result

            return {
                "status": True,
                "lam_x": lam_x,
                "lam_y": lam_y,
                "phi_x": phi_x,
                "beta": beta,
                "gamma": gamma,
                "var_e": np.diag(var_e),
                "var_e_x": np.diag(var_e_x),
                "var_e_y": np.diag(var_e_y),
            }
        else:
            return result

    except:
        return {
            "status": False,
            "msg": ''
        }



'''''
# 逻辑代码
# 参数x占1到24列数据  y占地25列数据
x = list(range(24))  # 用于生成 [0, 1, 2 ..., 23]
y = [24]

lam_x = np.array([
    [1, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 1],
])

lam_y = np.array([
    [1, 1, 1, 1, 1, 1],
    # [0, 0, 0, 0, 0, 0],
    # [0, 0, 0, 0, 0, 0],
    # [0, 0, 0, 0, 0, 0],
    # [0, 0, 0, 0, 0, 0],
    # [0, 0, 0, 0, 0, 0],

])

# 外生和内生变量之间的关系
gamma = np.array([
    [1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
])

# 内生潜变量之前的关系
beta = np.array([
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
])

# 从demo1中获取标准数据
data = np.loadtxt('data1701.xlsx.dat')


# 参数估计有下边的三种方法，需要选择哪个就去掉哪个中的注释

# 1.第一种方法---极大似然法
lam_x, lam_y, phi_x, beta, gamma, var_e, var_e_x, var_e_y = sem(
    data, y, x, lam_x, lam_y, beta, gamma)


# # 2. 第二种方法---最小二乘法
# lam_x, lam_y, phi_x, beta, gamma, var_e, var_e_x, var_e_y = sem(
#     data, y, x, lam_x, lam_y, beta, gamma, method='uls', step=0.001, max_iter=50000)


# 3. 第三种方法---广义最小二乘法
# lam_x, lam_y, phi_x, beta, gamma, var_e, var_e_x, var_e_y = sem(
#     data, y, x, lam_x, lam_y, beta, gamma, method='gls', step=0.001, max_iter=50000)

print('==========内源变量因子载荷=========')
print(lam_x)
print('=========外源变量因子载荷==========')
print(lam_y)
print('===========内源潜变量协方差矩阵=========')
print(phi_x)
print('============路径方程外源变量系数=========')
print(beta)
print('============路径方程内源变量系数=======')
print(gamma)
print('=============路径方程误差方差========')
print(np.diag(var_e))
print('============内源变量误差方差======')
print(np.diag(var_e_x))
print('=============外源变量误差方差=========')
print(np.diag(var_e_y))

'''''
