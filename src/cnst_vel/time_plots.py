import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import utils

import numpy as np
import matplotlib.pyplot as plt
import math
import utils_rl as utils
# import cvxpy as cp
from numpy.linalg import pinv, lstsq, svd, norm
from scipy.linalg import orthogonal_procrustes
import matplotlib as mpl
mpl.use('Qt5Agg')

np.set_printoptions(formatter={'float': lambda x: "{0:0.6f}".format(x)})

N_EXP = 100
SEED_START = 2110

def orientation_estimate(X1, X0, b):
    _, n = X0.shape
    I_n2 = np.identity(n * n)
    J = utils.commutation_matrix(n, n)
    Phi = (I_n2 + J) @ np.kron(X1.T, X0.T)
    vecH_ls = pinv(Phi.T @ Phi) @ Phi.T @ b
    # vecH_ls = lstsq(Phi, b)

    # svd and approximation
    # H_est = utils.vectorize_inverse(vecH)
    H_est_ls = utils.vectorize_inverse(vecH_ls)
    U, S, VT = svd(H_est_ls)
    H = U @ VT

    return H, H_est_ls

def procrustes_error(Z, Z_bar):
    H, scale = orthogonal_procrustes(Z.T, Z_bar.T)
    Z_proc = Z.T @ H
    # plt.figure()
    # plt.plot(Z_bar[0, :], Z_bar[1, :], 'bo')
    # plt.plot(Z_proc[:, 0], Z_proc[:, 1], 'ro')
    # plt.grid()
    # plt.show()
    err_z = utils.vectorize(Z_bar - Z_proc.T)

    return np.squeeze(err_z), H

if __name__ == "__main__":
    import pathlib

    save_flag = False
    noise_flag = True
    STD_DIST = 0.1
    OPTIONS = np.array([1, 1]) # first value for mc main and second for mc gtwr

    '''
        Trajectory generation
    '''
    # # from Anu: modification from Raj's case so as to not have the constraint that the first two nodes
    # # are relatively static
    Y0 = np.array([[-244.0, -588.0], [385.0, -456.0], [81.0, -992.0], [-19.0, -730.0], [-792.0, 879.0], [-554.0, 970.0],
                   [-965.0, 155.0], [-985.0, 318.0], [-49.0, -858.0], [-503.0, 419.0]]).transpose()
    Y1 = np.array(
        [[-5.0, -8.0], [-8.0, -5.0], [-6.0, -7.0], [6.0, -9.0], [-1.0, -3.0], [2.0, -2.0], [1.0, -2.0], [-5.0, -10.0],
         [9.0, 2.0], [-5.0, -1.0]]).transpose()

    # from Anu: modification from Raj's case so as to not have the constraint that the first two nodes
    # are relatively static
    # X0 = np.array([[-24.0, -58.0], [35.0, -45.0], [81.0, -29.0], [-19.0, -30.0], [-27.0, 79.0], [-54.0, 70.0],
    #                [-65.0, 15.0], [-45.0, 18.0], [-49.0, -58.0], [-50.0, 19.0]]).transpose()
    # Y1 = np.array(
    #     [[-2.0, -5.0], [-5.0, -2.0], [-3.0, -4.0], [3.0, -6.0], [-1.0, -3.0], [2.0, -2.0], [1.0, -2.0], [-2.0, -1.0],
    #      [4.0, 2.0], [-5.0, -1.0]]).transpose()

    # parameters
    K_array = np.array([10, 30, 50, 70, 90, 100])
    tend = 5.0

    # dimensions
    nDim, N = Y0.shape
    N_bar = int(N * (N - 1) / 2.)
    n_bar = int(N * (N + 1) / 2.)
    one = np.ones((N, 1))
    C = np.eye(N) - (one @ one.T) / N
    Y0_bar = Y0 @ C
    Y1_bar = Y1 @ C
    B0 = Y0_bar.T @ Y0_bar
    b0 = utils.half_vectorize(B0)
    B1 = Y0_bar.T @ Y1_bar + Y1_bar.T @ Y0_bar
    b1 = utils.half_vectorize(B1)
    B2 = Y1_bar.T @ Y1_bar
    b2 = utils.half_vectorize(B2)

    Sigma_d = STD_DIST ** 2 * np.identity(n_bar)
    Dm = utils.duplication_matrix_char(N)
    M = -0.5 * pinv(Dm) @ np.kron(C.T, C) @ Dm

    Y0_main_bar = np.zeros((nDim, N, N_EXP, len(K_array)))
    Y1_main_tilde = np.zeros((nDim, N, N_EXP, len(K_array)))
    H1_main = np.zeros((nDim, nDim, N_EXP, len(K_array)))
    err_main_b0 = np.zeros((n_bar, N_EXP, len(K_array)))
    err_main_b1 = np.zeros((n_bar, N_EXP, len(K_array)))
    err_main_b2 = np.zeros((n_bar, N_EXP, len(K_array)))
    err_main_y0 = np.zeros((nDim * N, N_EXP, len(K_array)))
    err_main_y1 = np.zeros((nDim * N, N_EXP, len(K_array)))
    rmse_main_b0 = np.zeros(len(K_array))
    rmse_main_b1 = np.zeros(len(K_array))
    rmse_main_b2 = np.zeros(len(K_array))
    rmse_main_y0 = np.zeros(len(K_array))
    rmse_main_y1 = np.zeros(len(K_array))

    for kk in range(len(K_array)):
        K = K_array[kk]
        print([kk, K])
        t_pwd = np.linspace(-tend, tend, K + 1).reshape(K + 1, 1)

        # Simulation
        X = np.zeros((nDim, N, K + 1))
        pwd = np.zeros((N, N, K + 1))
        pwd_noise = np.zeros((N, N, K + 1))

        for ii in range(K + 1):
            X[:, :, ii] = Y0 + Y1 * t_pwd[ii]
            pwd[:, :, ii] = utils.pairwise_distance(X[:, :, ii])

        for nn in range(N_EXP):
            # Adding measurement noise

            # noise = [] # To be used for monte carlo runs
            # assigning noise by using specific seeding
            np.random.seed(SEED_START + 10 * nn)
            n_EDM = int(N * (N - 1) / 2.)
            if noise_flag:
                noise_val = np.random.normal(0.0, STD_DIST, n_EDM * (K + 1))
            else:
                noise_val = np.zeros((n_EDM * (K + 1), 1))

            # var.append(sigmas.tolist())
            # noise.append(noise_val) # to be used for monte carlo runs

            D = np.zeros((N, N, K + 1))
            for ii in range(K + 1):
                vec_eta = noise_val[ii * n_EDM: (ii + 1) * n_EDM]
                eta = utils.half_vectorize_inverse(vec_eta, skew=True)
                # take square root of edm and then add noise, and then square afterwards
                pwd_noise[:, :, ii] = pwd[:, :, ii] + eta
                D[:, :, ii] = np.square(pwd_noise[:, :, ii])

            # Coefficient estimates
            # Forming matrix T
            n_bar = int(N * (N + 1) / 2.)
            I_nbar = np.identity(n_bar)
            T0 = np.kron(np.ones(t_pwd.shape), I_nbar)
            T1 = np.kron(t_pwd, I_nbar)
            T2 = np.kron(np.square(t_pwd), I_nbar)
            T = np.hstack((T0, T1, T2))

            # double-centering all EDMs to get their respective Gramians
            G = np.zeros((N, N, K + 1))
            vecG = np.zeros((n_bar * (K + 1), 1))
            for ii in range(K + 1):
                G[:, :, ii] = utils.double_center(D[:, :, ii])
                vecG[ii * n_bar: (ii + 1) * n_bar] = utils.half_vectorize(G[:, :, ii])

            # Solving for parameter theta
            # theta_hat_ls = pinv(T.T @ T) @ T.T @ vecG
            # theta_hat_ls = lstsq(T, vecG)

            # Weighted least squares
            Sigma_g = np.zeros((n_bar * (K + 1), n_bar * (K + 1)))
            w = np.zeros((K + 1) * n_bar)

            for ii in range(K + 1):
                d = utils.half_vectorize(pwd_noise[:, :, ii]).reshape(n_bar)
                Sigma_calD = 4. * np.diag(d) @ Sigma_d @ np.diag(d)
                Sigma_g[ii * n_bar: (ii + 1) * n_bar, ii * n_bar: (ii + 1) * n_bar] = M @ Sigma_calD @ M.T

            for jj in range(len(w)):
                w[jj] = 1 / Sigma_g[jj, jj]
            # theta_hat_ls = pinv(T.T @ np.diag(w) @ T) @ T.T @ np.diag(w) @ vecG
            Tw = np.diag(w) @ T
            vecGw = np.diag(w) @ vecG
            sol = lstsq(Tw, vecGw, rcond=None)
            theta_hat_ls = sol[0]

            b0_main = theta_hat_ls[:n_bar]
            err_main_b0[:, nn, kk] = np.squeeze(b0 - b0_main)
            B0_main = utils.half_vectorize_inverse(b0_main)

            b1_main = theta_hat_ls[n_bar:2*n_bar]
            err_main_b1[:, nn, kk] = np.squeeze(b1 - b1_main)
            B1_main = utils.half_vectorize_inverse(b1_main)

            b2_main = theta_hat_ls[2*n_bar:]
            err_main_b2[:, nn, kk] = np.squeeze(b2 - b2_main)
            B2_main = utils.half_vectorize_inverse(b2_main)

            # relative position - centered
            Y0_main_bar[:, :, nn, kk] = utils.cMDS(B0_main, center=False)[:nDim, :]
            err_main_y0[:, nn, kk], H_Y0 = procrustes_error(Y0_main_bar[:, :, nn, kk], Y0_bar)

            # relative velocity - centered with unknown rotation
            Y1_main_tilde[:, :, nn, kk] = utils.cMDS(B2_main, center=False)[:nDim, :]
            err_main_y1[:, nn, kk], H_Y1 = procrustes_error(Y1_main_tilde[:, :, nn, kk], Y1_bar)

            # Relative orientation
            vecB1_hat = utils.vectorize(B1_main)
            H1_main[:, :, nn, kk], H1_est = orientation_estimate(Y1_main_tilde[:, :, nn, kk], Y0_main_bar[:, :, nn, kk], vecB1_hat)
            Y1_bar_hat = H1_main[:, :, nn, kk] @ Y1_main_tilde[:, :, nn, kk]

    # True relative positions
    X0 = sim['position'][0]
    X0_bar = utils.align(X0)
    nDim, n = X0.shape
    _, rot = utils.rotate_and_check(sim['position'][0])

    one = np.ones((n, 1))
    C = np.identity(n) - one.dot(one.transpose()) / n

    X_true = []
    for ii in range(len(sim['position'])):
        X_tmp = sim['position'][ii].dot(C)
        rot = np.arctan2(X_tmp[1, 0], X_tmp[0, 0])
        X_tmp = np.array([[np.cos(rot), np.sin(rot)], [-np.sin(rot), np.cos(rot)]]).dot(X_tmp)
        X_true.append(X_tmp)

    X_est = []
    K = np.zeros((len(mc_results), 1))
    rmse_pos = np.zeros((len(t), len(mc_results)))
    for jj in range(len(mc_results)):
        K[jj] = mc_results[jj]['K']
        for ll in range(len(t)):
            # print([jj, t[ll]])
            e_norm_sum = 0.
            for kk in range(len(mc_results[jj]['position'])):
                X_tmp = mc_results[jj]['position'][kk]
                rot = np.arctan2(X_tmp[1, 0], X_tmp[0, 0])
                X_tmp = np.array([[np.cos(rot), np.sin(rot)], [-np.sin(rot), np.cos(rot)]]).dot(X_tmp)
                X_tmp[1, :] = -X_tmp[1, :]
                Y_tmp = mc_results[jj]['orientation'][kk].dot(mc_results[jj]['velocity'][kk])
                Y_tmp = np.array([[np.cos(rot), np.sin(rot)], [-np.sin(rot), np.cos(rot)]]).dot(Y_tmp)
                Y_tmp[1, :] = -Y_tmp[1, :]

                # plt.figure()
                # plt.plot(Y_tmp[0, :], Y_tmp[1, :], 'ro')
                # plt.plot(Y_true[0][0, :], Y_true[0][1, :], 'bo')
                # plt.show()

                E = X_tmp + Y_tmp * t[ll] - X_true[ll]
                e_norm_sum += np.linalg.norm(utils.vectorize(E)) ** 2

            rmse_pos[ll, jj] = np.sqrt(e_norm_sum / len(mc_results[jj]['position'])) / (nDim * n)

    plt.figure()
    # plt.semilogy(t, rmse_pos[:, 0], 'bo--', label='K = 40')
    # plt.semilogy(-t, rmse_pos[:, 0], 'bo--')
    # plt.semilogy(t, rmse_pos[:, 1], 'ro--', label='K = 70')
    # plt.semilogy(-t, rmse_pos[:, 1], 'ro--')
    plt.semilogy(t, rmse_pos[:, 2], 'mo--', label='K = 100')
    plt.semilogy(-t, rmse_pos[:, 2], 'mo--')
    plt.semilogy(t, cst.STD_DIST * np.ones(len(t)), 'ko')
    plt.semilogy(-t, cst.STD_DIST * np.ones(len(t)), 'ko')

    plt.grid(True)
    plt.legend()
    plt.show()

    print('finished!')