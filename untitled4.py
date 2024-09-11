# -*- coding: utf-8 -*-
"""Untitled4.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1HqlzPV8Gvz8HyGqu0ozPUXv3UT2d0A5G
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.covariance import LedoitWolf, OAS, EmpiricalCovariance
from numpy.linalg import norm

def generate_ar1(p, n, rho=0.5):
    """Generate an AR(1) process with parameter rho."""
    timeseries = np.random.randn(n, p)
    for i in range(1, p):
        timeseries[:, i] = rho * timeseries[:, i - 1] + np.sqrt(1 - rho**2) * np.random.randn(n)
    return np.cov(timeseries, rowvar=False)

def generate_fbm(p, n, H=0.75):
    """Generate Fractional Brownian Motion using Cholesky decomposition."""
    cov_matrix = np.zeros((p, p))
    for i in range(p):
        for j in range(i + 1):
            cov_matrix[i, j] = 0.5 * ((i + 1)**(2 * H) + (j + 1)**(2 * H) - abs(i - j)**(2 * H))
            cov_matrix[j, i] = cov_matrix[i, j]

    cholesky_decomp = np.linalg.cholesky(cov_matrix)
    fbm_samples = np.dot(np.random.randn(n, p), cholesky_decomp)
    return np.cov(fbm_samples, rowvar=False)

def estimator_metrics(sample, Sigma):
    """Calculate estimator metrics: shrinkage coefficients and MSE for different methods."""
    # Sample Covariance
    S = np.cov(sample.T)
    mse_s = norm(S - Sigma, 'fro')**2

    # Ledoit-Wolf
    lw = LedoitWolf().fit(sample)
    Sigma_hat_lw = lw.covariance_
    mse_lw = norm(Sigma_hat_lw - Sigma, 'fro')**2
    shrinkage_lw = lw.shrinkage_

    # Rao-Blackwell Ledoit-Wolf (RBLW)
    rblw = LedoitWolf(store_precision=True).fit(sample)
    mse_rblw = norm(rblw.covariance_ - Sigma, 'fro')**2
    shrinkage_rblw = rblw.shrinkage_

    # Oracle Approximating Shrinkage (OAS)
    oas = OAS().fit(sample)
    Sigma_hat_oas = oas.covariance_
    mse_oas = norm(Sigma_hat_oas - Sigma, 'fro')**2
    shrinkage_oas = oas.shrinkage_

    # Oracle Estimator (Shrinkage to Identity)
    F = np.eye(S.shape[0]) * np.trace(S) / S.shape[0]
    rho_oracle = (S.shape[0] - 1) / S.shape[0]
    Sigma_hat_oracle = rho_oracle * F + (1 - rho_oracle) * S
    mse_oracle = norm(Sigma_hat_oracle - Sigma, 'fro')**2
    shrinkage_oracle = rho_oracle

    return {
        'mse': {'Sample': mse_s, 'LW': mse_lw, 'RBLW': mse_rblw, 'OAS': mse_oas, 'Oracle': mse_oracle},
        'shrinkage': {'LW': shrinkage_lw, 'RBLW': shrinkage_rblw, 'OAS': shrinkage_oas, 'Oracle': shrinkage_oracle}
    }

def simulate_estimators(p, n, num_simulations=100, process_type='ar1', rho=0.5, H=0.75):
    results = {'mse': {key: [] for key in ['Sample', 'LW', 'RBLW', 'OAS', 'Oracle']},
               'shrinkage': {key: [] for key in ['LW', 'RBLW', 'OAS', 'Oracle']}}

    for _ in range(num_simulations):
        if process_type == 'ar1':
            Sigma = generate_ar1(p, n, rho)
        elif process_type == 'fbm':
            Sigma = generate_fbm(p, n, H)

        sample = np.random.multivariate_normal(np.zeros(p), Sigma, size=n)
        metrics = estimator_metrics(sample, Sigma)

        for metric_type in results:
            for estimator in results[metric_type]:
                results[metric_type][estimator].append(metrics[metric_type][estimator])

    return {metric: {est: np.mean(vals) for est, vals in ests.items()} for metric, ests in results.items()}

# Parameters
p = 100  # Dimensionality
sample_sizes = [5, 10, 20, 50, 100, 120]  # Sample sizes
# Defining the processes
processes = {
    'AR(1)': {'process_type': 'ar1', 'rho': 0.5},
    'FBM': {'process_type': 'fbm', 'H': 0.5}
}

# Plotting the results
fig, axes = plt.subplots(2, 2, figsize=(14, 12))
fig.suptitle('Estimator Comparisons for AR(1) and FBM Processes')

# Loop through the processes and sample sizes
for i, (process_name, params) in enumerate(processes.items()):
    mse_results = {key: [] for key in ['Sample', 'LW', 'RBLW', 'OAS', 'Oracle']}
    shrinkage_results = {key: [] for key in ['LW', 'RBLW', 'OAS', 'Oracle']}

    for n in sample_sizes:
        # Simulate estimators for each sample size
        results = simulate_estimators(p, n, **params)

        for est in mse_results:
            mse_results[est].append(results['mse'][est])

        for est in shrinkage_results:
            if est in results['shrinkage']:  # Not all methods have shrinkage
                shrinkage_results[est].append(results['shrinkage'][est])

    # Plot MSE results for this process
    ax = axes[i, 0]
    for key, mse_vals in mse_results.items():
        ax.plot(sample_sizes, mse_vals, label=f'{key} MSE')
    ax.set_title(f'{process_name} Process MSE')
    ax.set_xlabel('Sample Size (n)')
    ax.set_ylabel('Mean Squared Error')
    ax.legend()

    # Plot shrinkage results for this process
    ax = axes[i, 1]
    for key, shrink_vals in shrinkage_results.items():
        ax.plot(sample_sizes, shrink_vals, label=f'{key} Shrinkage')
    ax.set_title(f'{process_name} Process Shrinkage')
    ax.set_xlabel('Sample Size (n)')
    ax.set_ylabel('Shrinkage Coefficient')
    ax.legend()

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()

# Plotting the results with dot markers
fig, axes = plt.subplots(2, 2, figsize=(14, 12))
fig.suptitle('Estimator Comparisons for AR(1) and FBM Processes')

# Loop through the processes and sample sizes
for i, (process_name, params) in enumerate(processes.items()):
    mse_results = {key: [] for key in ['Sample', 'LW', 'RBLW', 'OAS', 'Oracle']}
    shrinkage_results = {key: [] for key in ['LW', 'RBLW', 'OAS', 'Oracle']}

    for n in sample_sizes:
        # Simulate estimators for each sample size
        results = simulate_estimators(p, n, **params)

        for est in mse_results:
            mse_results[est].append(results['mse'][est])

        for est in shrinkage_results:
            if est in results['shrinkage']:  # Not all methods have shrinkage
                shrinkage_results[est].append(results['shrinkage'][est])

    # Plot MSE results for this process with dot markers
    ax = axes[i, 0]
    for key, mse_vals in mse_results.items():
        ax.plot(sample_sizes, mse_vals, marker='o', label=f'{key} MSE')  # Added 'o' for dots
    ax.set_title(f'{process_name} Process MSE')
    ax.set_xlabel('Sample Size (n)')
    ax.set_ylabel('Mean Squared Error')
    ax.legend()

    # Plot shrinkage results for this process with dot markers
    ax = axes[i, 1]
    for key, shrink_vals in shrinkage_results.items():
        ax.plot(sample_sizes, shrink_vals, marker='o', label=f'{key} Shrinkage')  # Added 'o' for dots
    ax.set_title(f'{process_name} Process Shrinkage')
    ax.set_xlabel('Sample Size (n)')
    ax.set_ylabel('Shrinkage Coefficient')
    ax.legend()

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()

import numpy as np
import matplotlib.pyplot as plt
from sklearn.covariance import LedoitWolf, OAS, EmpiricalCovariance
from numpy.linalg import norm

# Define DOASD Estimator
class DOASD:
    def __init__(self, diagonal_shrinkage=0.4, off_diagonal_shrinkage=0.3):
        self.diagonal_shrinkage = diagonal_shrinkage
        self.off_diagonal_shrinkage = off_diagonal_shrinkage

    def fit(self, X):
        emp_cov = np.cov(X, rowvar=False)
        shrunk_diag_cov = emp_cov * (1 - self.diagonal_shrinkage) + np.diag(np.diag(emp_cov)) * self.diagonal_shrinkage
        self.covariance_ = shrunk_diag_cov * (1 - self.off_diagonal_shrinkage) + np.diag(np.diag(shrunk_diag_cov)) * self.off_diagonal_shrinkage
        return self

# Define DualShrinkageEstimator
class DualShrinkageEstimator:
    def __init__(self, delta_diag=0.4, delta_off_diag=0.3):
        self.delta_diag = delta_diag
        self.delta_off_diag = delta_off_diag

    def fit(self, X):
        sample_cov = np.cov(X, rowvar=False)
        D = np.diag(np.diag(sample_cov))
        O = sample_cov - D
        diag_target = np.diag(np.var(X, axis=0))
        off_diag_target = np.zeros_like(O)
        shrunk_diag = self.delta_diag * D + (1 - self.delta_diag) * diag_target
        shrunk_off_diag = self.delta_off_diag * O + (1 - self.delta_off_diag) * off_diag_target
        self.covariance_ = shrunk_diag + shrunk_off_diag
        return self

# Define Schafer-Strimmer Estimator
class SchaferStrimmer:
    def __init__(self, shrinkage=0.4):
        self.shrinkage = shrinkage

    def fit(self, X):
        emp_cov = np.cov(X, rowvar=False)
        I = np.eye(emp_cov.shape[0])
        self.covariance_ = (1 - self.shrinkage) * emp_cov + self.shrinkage * I * np.trace(emp_cov) / emp_cov.shape[0]
        return self

# Generate AR(1) and FBM processes
def generate_ar1(p, n, rho=0.5):
    timeseries = np.random.randn(n, p)
    for i in range(1, p):
        timeseries[:, i] = rho * timeseries[:, i - 1] + np.sqrt(1 - rho**2) * np.random.randn(n)
    return np.cov(timeseries, rowvar=False)

def generate_fbm(p, n, H=0.75):
    cov_matrix = np.zeros((p, p))
    for i in range(p):
        for j in range(i + 1):
            cov_matrix[i, j] = 0.5 * ((i + 1)**(2 * H) + (j + 1)**(2 * H) - abs(i - j)**(2 * H))
            cov_matrix[j, i] = cov_matrix[i, j]

    cholesky_decomp = np.linalg.cholesky(cov_matrix)
    fbm_samples = np.dot(np.random.randn(n, p), cholesky_decomp)
    return np.cov(fbm_samples, rowvar=False)

# Estimator metrics function
def estimator_metrics(sample, Sigma):
    S = np.cov(sample.T)
    mse_s = norm(S - Sigma, 'fro')**2

    # Ledoit-Wolf
    lw = LedoitWolf().fit(sample)
    mse_lw = norm(lw.covariance_ - Sigma, 'fro')**2

    # OAS
    oas = OAS().fit(sample)
    mse_oas = norm(oas.covariance_ - Sigma, 'fro')**2

    # DOASD
    doasd = DOASD().fit(sample)
    mse_doasd = norm(doasd.covariance_ - Sigma, 'fro')**2

    # DualShrinkage
    dual_shrinkage = DualShrinkageEstimator().fit(sample)
    mse_dual_shrinkage = norm(dual_shrinkage.covariance_ - Sigma, 'fro')**2

    # Schafer-Strimmer
    ss = SchaferStrimmer().fit(sample)
    mse_ss = norm(ss.covariance_ - Sigma, 'fro')**2

    return {
        'mse': {'Sample': mse_s, 'LW': mse_lw, 'OAS': mse_oas, 'DOASD': mse_doasd, 'DualShrinkage': mse_dual_shrinkage, 'Schafer-Strimmer': mse_ss}
    }

# Simulation function
def simulate_estimators(p, n, num_simulations=100, process_type='ar1', rho=0.5, H=0.75):
    results = {'mse': {key: [] for key in ['Sample', 'LW', 'OAS', 'DOASD', 'DualShrinkage', 'Schafer-Strimmer']}}

    for _ in range(num_simulations):
        if process_type == 'ar1':
            Sigma = generate_ar1(p, n, rho)
        elif process_type == 'fbm':
            Sigma = generate_fbm(p, n, H)

        sample = np.random.multivariate_normal(np.zeros(p), Sigma, size=n)
        metrics = estimator_metrics(sample, Sigma)

        for metric_type in results:
            for estimator in results[metric_type]:
                results[metric_type][estimator].append(metrics[metric_type][estimator])

    return {metric: {est: np.mean(vals) for est, vals in ests.items()} for metric, ests in results.items()}

# Parameters and processes
p = 100
sample_sizes = [5, 10, 20, 50, 100, 120]
processes = {'AR(1)': {'process_type': 'ar1', 'rho': 0.5}, 'FBM': {'process_type': 'fbm', 'H': 0.75}}

# Plotting results
fig, axes = plt.subplots(2, 2, figsize=(14, 12))
fig.suptitle('Estimator Comparisons for AR(1) and FBM Processes')

for i, (process_name, params) in enumerate(processes.items()):
    mse_results = {key: [] for key in ['Sample', 'LW', 'OAS', 'DOASD', 'DualShrinkage', 'Schafer-Strimmer']}

    for n in sample_sizes:
        results = simulate_estimators(p, n, **params)
        for est in mse_results:
            mse_results[est].append(results['mse'][est])

    # Plot MSE for each estimator
    ax = axes[i, 0]
    for key, mse_vals in mse_results.items():
        ax.plot(sample_sizes, mse_vals, label=f'{key} MSE')
    ax.set_title(f'{process_name} Process MSE')
    ax.set_xlabel('Sample Size (n)')
    ax.set_ylabel('Mean Squared Error')
    ax.legend()

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()

import numpy as np
import matplotlib.pyplot as plt
from sklearn.covariance import LedoitWolf, OAS, EmpiricalCovariance
from numpy.linalg import norm

# Define DOASD Estimator
class DOASD:
    def __init__(self, diagonal_shrinkage=0.4, off_diagonal_shrinkage=0.3):
        self.diagonal_shrinkage = diagonal_shrinkage
        self.off_diagonal_shrinkage = off_diagonal_shrinkage

    def fit(self, X):
        emp_cov = np.cov(X, rowvar=False)
        shrunk_diag_cov = emp_cov * (1 - self.diagonal_shrinkage) + np.diag(np.diag(emp_cov)) * self.diagonal_shrinkage
        self.covariance_ = shrunk_diag_cov * (1 - self.off_diagonal_shrinkage) + np.diag(np.diag(shrunk_diag_cov)) * self.off_diagonal_shrinkage
        return self

# Define DualShrinkageEstimator
class DualShrinkageEstimator:
    def __init__(self, delta_diag=0.4, delta_off_diag=0.3):
        self.delta_diag = delta_diag
        self.delta_off_diag = delta_off_diag

    def fit(self, X):
        sample_cov = np.cov(X, rowvar=False)
        D = np.diag(np.diag(sample_cov))
        O = sample_cov - D
        diag_target = np.diag(np.var(X, axis=0))
        off_diag_target = np.zeros_like(O)
        shrunk_diag = self.delta_diag * D + (1 - self.delta_diag) * diag_target
        shrunk_off_diag = self.delta_off_diag * O + (1 - self.delta_off_diag) * off_diag_target
        self.covariance_ = shrunk_diag + shrunk_off_diag
        return self

# Define Schafer-Strimmer Estimator
class SchaferStrimmer:
    def __init__(self, shrinkage=0.4):
        self.shrinkage = shrinkage

    def fit(self, X):
        emp_cov = np.cov(X, rowvar=False)
        I = np.eye(emp_cov.shape[0])
        self.covariance_ = (1 - self.shrinkage) * emp_cov + self.shrinkage * I * np.trace(emp_cov) / emp_cov.shape[0]
        return self

# Generate AR(1) and FBM processes
def generate_ar1(p, n, rho=0.5):
    timeseries = np.random.randn(n, p)
    for i in range(1, p):
        timeseries[:, i] = rho * timeseries[:, i - 1] + np.sqrt(1 - rho**2) * np.random.randn(n)
    return np.cov(timeseries, rowvar=False)

def generate_fbm(p, n, H=0.75):
    cov_matrix = np.zeros((p, p))
    for i in range(p):
        for j in range(i + 1):
            cov_matrix[i, j] = 0.5 * ((i + 1)**(2 * H) + (j + 1)**(2 * H) - abs(i - j)**(2 * H))
            cov_matrix[j, i] = cov_matrix[i, j]

    cholesky_decomp = np.linalg.cholesky(cov_matrix)
    fbm_samples = np.dot(np.random.randn(n, p), cholesky_decomp)
    return np.cov(fbm_samples, rowvar=False)

# Estimator metrics function
def estimator_metrics(sample, Sigma):
    S = np.cov(sample.T)
    mse_s = norm(S - Sigma, 'fro')**2

    # Ledoit-Wolf
    lw = LedoitWolf().fit(sample)
    mse_lw = norm(lw.covariance_ - Sigma, 'fro')**2
    shrinkage_lw = lw.shrinkage_

    # OAS
    oas = OAS().fit(sample)
    mse_oas = norm(oas.covariance_ - Sigma, 'fro')**2
    shrinkage_oas = oas.shrinkage_

    # DOASD
    doasd = DOASD().fit(sample)
    mse_doasd = norm(doasd.covariance_ - Sigma, 'fro')**2
    shrinkage_doasd = doasd.diagonal_shrinkage  # Example of extracting shrinkage

    # DualShrinkage
    dual_shrinkage = DualShrinkageEstimator().fit(sample)
    mse_dual_shrinkage = norm(dual_shrinkage.covariance_ - Sigma, 'fro')**2
    shrinkage_dual_shrinkage = dual_shrinkage.delta_diag  # Example of extracting shrinkage

    # Schafer-Strimmer
    ss = SchaferStrimmer().fit(sample)
    mse_ss = norm(ss.covariance_ - Sigma, 'fro')**2
    shrinkage_ss = ss.shrinkage  # Example of extracting shrinkage

    # Oracle Estimator (Shrinkage to Identity)
    F = np.eye(S.shape[0]) * np.trace(S) / S.shape[0]
    rho_oracle = (S.shape[0] - 1) / S.shape[0]
    Sigma_hat_oracle = rho_oracle * F + (1 - rho_oracle) * S
    mse_oracle = norm(Sigma_hat_oracle - Sigma, 'fro')**2
    shrinkage_oracle = rho_oracle

    return {
        'mse': {'Sample': mse_s, 'LW': mse_lw, 'OAS': mse_oas, 'DOASD': mse_doasd, 'DualShrinkage': mse_dual_shrinkage, 'Schafer-Strimmer': mse_ss, 'Oracle': mse_oracle},
        'shrinkage': {'LW': shrinkage_lw, 'OAS': shrinkage_oas, 'DOASD': shrinkage_doasd, 'DualShrinkage': shrinkage_dual_shrinkage, 'Schafer-Strimmer': shrinkage_ss, 'Oracle': shrinkage_oracle}
    }

# Simulation function
def simulate_estimators(p, n, num_simulations=100, process_type='ar1', rho=0.5, H=0.75):
    results = {'mse': {key: [] for key in ['Sample', 'LW', 'OAS', 'DOASD', 'DualShrinkage', 'Schafer-Strimmer', 'Oracle']},
               'shrinkage': {key: [] for key in ['LW', 'OAS', 'DOASD', 'DualShrinkage', 'Schafer-Strimmer', 'Oracle']}}

    for _ in range(num_simulations):
        if process_type == 'ar1':
            Sigma = generate_ar1(p, n, rho)
        elif process_type == 'fbm':
            Sigma = generate_fbm(p, n, H)

        sample = np.random.multivariate_normal(np.zeros(p), Sigma, size=n)
        metrics = estimator_metrics(sample, Sigma)

        for metric_type in results:
            for estimator in results[metric_type]:
                results[metric_type][estimator].append(metrics[metric_type][estimator])

    return {metric: {est: np.mean(vals) for est, vals in ests.items()} for metric, ests in results.items()}

# Parameters and processes
p = 100
sample_sizes = [5, 10, 20, 50, 100, 120]
processes = {'AR(1)': {'process_type': 'ar1', 'rho': 0.5}, 'FBM': {'process_type': 'fbm', 'H': 0.75}}

# Plotting results
fig, axes = plt.subplots(2, 2, figsize=(14, 12))
fig.suptitle('Estimator Comparisons for AR(1) and FBM Processes')

for i, (process_name, params) in enumerate(processes.items()):
    mse_results = {key: [] for key in ['Sample', 'LW', 'OAS', 'DOASD', 'DualShrinkage', 'Schafer-Strimmer', 'Oracle']}
    shrinkage_results = {key: [] for key in ['LW', 'OAS', 'DOASD', 'DualShrinkage', 'Schafer-Strimmer', 'Oracle']}

    for n in sample_sizes:
        results = simulate_estimators(p, n, **params)

        for est in mse_results:
            mse_results[est].append(results['mse'][est])

        for est in shrinkage_results:
            if est in results['shrinkage']:  # Not all methods have shrinkage
                shrinkage_results[est].append(results['shrinkage'][est])

    # Plot MSE for each estimator
    ax = axes[i, 0]
    for est in mse_results:
        ax.plot(sample_sizes, mse_results[est], label=est)
    ax.set_title(f'{process_name} - MSE')
    ax.set_xlabel('Sample Size')
    ax.set_ylabel('MSE')
    ax.legend()

    # Plot Shrinkage for each estimator
    if shrinkage_results:
        ax = axes[i, 1]
        for est in shrinkage_results:
            ax.plot(sample_sizes, shrinkage_results[est], label=est)
        ax.set_title(f'{process_name} - Shrinkage')
        ax.set_xlabel('Sample Size')
        ax.set_ylabel('Shrinkage')
        ax.legend()

plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.show()

import numpy as np
import matplotlib.pyplot as plt
from sklearn.covariance import LedoitWolf, OAS, EmpiricalCovariance
from numpy.linalg import norm

# Define DOASD Estimator
class DOASD:
    def __init__(self, diagonal_shrinkage=0.4, off_diagonal_shrinkage=0.3):
        self.diagonal_shrinkage = diagonal_shrinkage
        self.off_diagonal_shrinkage = off_diagonal_shrinkage

    def fit(self, X):
        emp_cov = np.cov(X, rowvar=False)
        shrunk_diag_cov = emp_cov * (1 - self.diagonal_shrinkage) + np.diag(np.diag(emp_cov)) * self.diagonal_shrinkage
        self.covariance_ = shrunk_diag_cov * (1 - self.off_diagonal_shrinkage) + np.diag(np.diag(shrunk_diag_cov)) * self.off_diagonal_shrinkage
        return self

# Define DualShrinkageEstimator
class DualShrinkageEstimator:
    def __init__(self, delta_diag=0.4, delta_off_diag=0.3):
        self.delta_diag = delta_diag
        self.delta_off_diag = delta_off_diag

    def fit(self, X):
        sample_cov = np.cov(X, rowvar=False)
        D = np.diag(np.diag(sample_cov))
        O = sample_cov - D
        diag_target = np.diag(np.var(X, axis=0))
        off_diag_target = np.zeros_like(O)
        shrunk_diag = self.delta_diag * D + (1 - self.delta_diag) * diag_target
        shrunk_off_diag = self.delta_off_diag * O + (1 - self.delta_off_diag) * off_diag_target
        self.covariance_ = shrunk_diag + shrunk_off_diag
        return self

# Define Schafer-Strimmer Estimator
class SchaferStrimmer:
    def __init__(self, shrinkage=0.4):
        self.shrinkage = shrinkage

    def fit(self, X):
        emp_cov = np.cov(X, rowvar=False)
        I = np.eye(emp_cov.shape[0])
        self.covariance_ = (1 - self.shrinkage) * emp_cov + self.shrinkage * I * np.trace(emp_cov) / emp_cov.shape[0]
        return self

# Generate AR(1) and FBM processes
def generate_ar1(p, n, rho=0.5):
    timeseries = np.random.randn(n, p)
    for i in range(1, p):
        timeseries[:, i] = rho * timeseries[:, i - 1] + np.sqrt(1 - rho**2) * np.random.randn(n)
    return np.cov(timeseries, rowvar=False)

def generate_fbm(p, n, H=0.75):
    cov_matrix = np.zeros((p, p))
    for i in range(p):
        for j in range(i + 1):
            cov_matrix[i, j] = 0.5 * ((i + 1)**(2 * H) + (j + 1)**(2 * H) - abs(i - j)**(2 * H))
            cov_matrix[j, i] = cov_matrix[i, j]

    cholesky_decomp = np.linalg.cholesky(cov_matrix)
    fbm_samples = np.dot(np.random.randn(n, p), cholesky_decomp)
    return np.cov(fbm_samples, rowvar=False)

# Estimator metrics function
def estimator_metrics(sample, Sigma):
    S = np.cov(sample.T)
    mse_s = norm(S - Sigma, 'fro')**2

    # Ledoit-Wolf
    lw = LedoitWolf().fit(sample)
    mse_lw = norm(lw.covariance_ - Sigma, 'fro')**2
    shrinkage_lw = lw.shrinkage_

    # Rao-Blackwell Ledoit-Wolf (RBLW)
    rblw = LedoitWolf(store_precision=True).fit(sample)
    mse_rblw = norm(rblw.covariance_ - Sigma, 'fro')**2
    shrinkage_rblw = rblw.shrinkage_

    # OAS
    oas = OAS().fit(sample)
    mse_oas = norm(oas.covariance_ - Sigma, 'fro')**2
    shrinkage_oas = oas.shrinkage_

    # DOASD
    doasd = DOASD().fit(sample)
    mse_doasd = norm(doasd.covariance_ - Sigma, 'fro')**2
    shrinkage_doasd = doasd.diagonal_shrinkage  # Example of extracting shrinkage

    # DualShrinkage
    dual_shrinkage = DualShrinkageEstimator().fit(sample)
    mse_dual_shrinkage = norm(dual_shrinkage.covariance_ - Sigma, 'fro')**2
    shrinkage_dual_shrinkage = dual_shrinkage.delta_diag  # Example of extracting shrinkage

    # Schafer-Strimmer
    ss = SchaferStrimmer().fit(sample)
    mse_ss = norm(ss.covariance_ - Sigma, 'fro')**2
    shrinkage_ss = ss.shrinkage  # Example of extracting shrinkage

    # Oracle Estimator (Shrinkage to Identity)
    F = np.eye(S.shape[0]) * np.trace(S) / S.shape[0]
    rho_oracle = (S.shape[0] - 1) / S.shape[0]
    Sigma_hat_oracle = rho_oracle * F + (1 - rho_oracle) * S
    mse_oracle = norm(Sigma_hat_oracle - Sigma, 'fro')**2
    shrinkage_oracle = rho_oracle

    return {
        'mse': {'Sample': mse_s, 'LW': mse_lw, 'RBLW': mse_rblw, 'OAS': mse_oas, 'DOASD': mse_doasd, 'DualShrinkage': mse_dual_shrinkage, 'Schafer-Strimmer': mse_ss, 'Oracle': mse_oracle},
        'shrinkage': {'LW': shrinkage_lw, 'RBLW': shrinkage_rblw, 'OAS': shrinkage_oas, 'DOASD': shrinkage_doasd, 'DualShrinkage': shrinkage_dual_shrinkage, 'Schafer-Strimmer': shrinkage_ss, 'Oracle': shrinkage_oracle}
    }

# Simulation function
def simulate_estimators(p, n, num_simulations=100, process_type='ar1', rho=0.5, H=0.75):
    results = {'mse': {key: [] for key in ['Sample', 'LW', 'RBLW', 'OAS', 'DOASD', 'DualShrinkage', 'Schafer-Strimmer', 'Oracle']},
               'shrinkage': {key: [] for key in ['LW', 'RBLW', 'OAS', 'DOASD', 'DualShrinkage', 'Schafer-Strimmer', 'Oracle']}}

    for _ in range(num_simulations):
        if process_type == 'ar1':
            Sigma = generate_ar1(p, n, rho)
        elif process_type == 'fbm':
            Sigma = generate_fbm(p, n, H)

        sample = np.random.multivariate_normal(np.zeros(p), Sigma, size=n)
        metrics = estimator_metrics(sample, Sigma)

        for metric_type in results:
            for estimator in results[metric_type]:
                results[metric_type][estimator].append(metrics[metric_type][estimator])

    return {metric: {est: np.mean(vals) for est, vals in ests.items()} for metric, ests in results.items()}

# Parameters and processes
p = 100
sample_sizes = [5, 10, 20, 50, 100, 120]
processes = {'AR(1)': {'process_type': 'ar1', 'rho': 0.5}, 'FBM': {'process_type': 'fbm', 'H': 0.75}}

# Plotting results
fig, axes = plt.subplots(2, 2, figsize=(14, 12))
fig.suptitle('Estimator Comparisons for AR(1) and FBM Processes')

for i, (process_name, params) in enumerate(processes.items()):
    mse_results = {key: [] for key in ['Sample', 'LW', 'RBLW', 'OAS', 'DOASD', 'DualShrinkage', 'Schafer-Strimmer', 'Oracle']}
    shrinkage_results = {key: [] for key in ['LW', 'RBLW', 'OAS', 'DOASD', 'DualShrinkage', 'Schafer-Strimmer', 'Oracle']}

    for n in sample_sizes:
        results = simulate_estimators(p, n, **params)

        for est in mse_results:
            mse_results[est].append(results['mse'][est])

        for est in shrinkage_results:
            if est in results['shrinkage']:
                shrinkage_results[est].append(results['shrinkage'][est])

    # Plot MSE results for this process
    ax = axes[i, 0]
    for est in mse_results:
        ax.plot(sample_sizes, mse_results[est], label=est)
    ax.set_title(f'{process_name} - MSE')
    ax.set_xlabel('Sample Size')
    ax.set_ylabel('MSE')
    ax.legend()

    # Plot Shrinkage for each estimator
    if shrinkage_results:
        ax = axes[i, 1]
        for est in shrinkage_results:
            ax.plot(sample_sizes, shrinkage_results[est], label=est)
        ax.set_title(f'{process_name} - Shrinkage')
        ax.set_xlabel('Sample Size')
        ax.set_ylabel('Shrinkage')
        ax.legend()

plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.show()

# Plotting results
fig, axes = plt.subplots(2, 2, figsize=(14, 12))
fig.suptitle('Estimator Comparisons for AR(1) and FBM Processes')

for i, (process_name, params) in enumerate(processes.items()):
    mse_results = {key: [] for key in ['Sample', 'LW', 'RBLW', 'OAS', 'DOASD', 'DualShrinkage', 'Schafer-Strimmer', 'Oracle']}
    shrinkage_results = {key: [] for key in ['LW', 'RBLW', 'OAS', 'DOASD', 'DualShrinkage', 'Schafer-Strimmer', 'Oracle']}

    for n in sample_sizes:
        results = simulate_estimators(p, n, **params)

        for est in mse_results:
            mse_results[est].append(results['mse'][est])

        for est in shrinkage_results:
            if est in results['shrinkage']:
                shrinkage_results[est].append(results['shrinkage'][est])

    # Plot MSE results for this process with dots
    ax = axes[i, 0]
    for est in mse_results:
        ax.plot(sample_sizes, mse_results[est], marker='o', label=est)  # Adding dots to the line
    ax.set_title(f'{process_name} - MSE')
    ax.set_xlabel('Sample Size')
    ax.set_ylabel('MSE')
    ax.legend()

    # Plot Shrinkage for each estimator with dots
    if shrinkage_results:
        ax = axes[i, 1]
        for est in shrinkage_results:
            ax.plot(sample_sizes, shrinkage_results[est], marker='o', label=est)  # Adding dots to the line
        ax.set_title(f'{process_name} - Shrinkage')
        ax.set_xlabel('Sample Size')
        ax.set_ylabel('Shrinkage')
        ax.legend()

plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.show()

