import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from IPython.display import display
from sklearn.decomposition import PCA, FactorAnalysis
from sklearn.preprocessing import StandardScaler

from scripts.constants import PRIMARY_POS_ORDER


def explore_dimensionality_reduction(df, columns, group_col='Primary_Pos', palette=None, k=None):
    columns = list(columns)
    plot_df = df[columns + [group_col]].dropna()
    scaler = StandardScaler()
    X = scaler.fit_transform(plot_df[columns])

    if palette is None:
        groups = sorted(plot_df[group_col].unique())
        order = [p for p in PRIMARY_POS_ORDER if p in groups] + [p for p in groups if p not in PRIMARY_POS_ORDER]
        palette = dict(zip(order, sns.color_palette('tab10', n_colors=len(order))))

    # 1. Scree plot (full PCA) - pick k via the elbow heuristic: the component furthest
    # below the line joining the first and last eigenvalue is the bend; keep everything before it
    eigenvalues = PCA().fit(X).explained_variance_
    comps = np.arange(1, len(eigenvalues) + 1)

    x_norm = (comps - comps.min()) / (comps.max() - comps.min())
    y_norm = (eigenvalues - eigenvalues.min()) / (eigenvalues.max() - eigenvalues.min())
    line_vec = np.array([x_norm[-1] - x_norm[0], y_norm[-1] - y_norm[0]])
    line_vec /= np.linalg.norm(line_vec)
    vec_from_first = np.stack([x_norm - x_norm[0], y_norm - y_norm[0]], axis=1)
    vec_parallel = np.outer(vec_from_first @ line_vec, line_vec)
    dist_from_line = np.linalg.norm(vec_from_first - vec_parallel, axis=1)
    elbow = int(np.argmax(dist_from_line)) + 1
    
    if k is None:
        k = max(1, elbow - 1)
    else:
        k = int(k)
        
    kaiser_k = int((eigenvalues > 1).sum())

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(comps, eigenvalues, 'o-', color='teal')
    ax.axhline(1, color='#4C72B0', linestyle='--', linewidth=1, label=f'Kaiser criterion (k={kaiser_k})')
    ax.axvline(elbow, color='#898781', linestyle='--', linewidth=1, label=f'Elbow (component {elbow})')
    ax.axvline(k, color='#C44E52', linestyle=':', linewidth=1.5, label=f'Chosen k = {k}')
    ax.set_xlabel('Component')
    ax.set_ylabel('Eigenvalue')
    ax.set_title('Scree Plot', fontsize=14, fontweight='bold')
    ax.set_xticks(comps)
    ax.legend()
    plt.tight_layout()
    plt.show()

    # 2. Variance explained by each component/factor - show at least 5 (or all available columns), even
    # though only k are kept above; FA components aren't nested like PCA's, so these are refit at n_show
    n_show = max(k, min(5, len(columns)))
    pca_show = PCA(n_components=n_show).fit(X)
    fa_show = FactorAnalysis(n_components=n_show, random_state=0).fit(X)
    pca_var_ratio = pca_show.explained_variance_ratio_
    fa_var_ratio = (fa_show.components_ ** 2).sum(axis=1) / len(columns)  # sum of squared loadings, as a share of total variance
    show_comps = np.arange(1, n_show + 1)

    width = 0.35
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(show_comps - width / 2, pca_var_ratio * 100, width, color='teal', label='PCA')
    ax.bar(show_comps + width / 2, fa_var_ratio * 100, width, color='#3F51B5', label='Factor Analysis')
    for x, v in zip(show_comps - width / 2, pca_var_ratio * 100):
        ax.text(x, v, f'{v:.1f}%', ha='center', va='bottom', fontsize=8)
    for x, v in zip(show_comps + width / 2, fa_var_ratio * 100):
        ax.text(x, v, f'{v:.1f}%', ha='center', va='bottom', fontsize=8)
    ax.set_xticks(show_comps)
    ax.set_xlabel('Component / Factor')
    ax.set_ylabel('% Variance Explained')
    ax.set_title('Variance Explained', fontsize=14, fontweight='bold')
    ax.legend()
    plt.tight_layout()
    plt.show()

    # 3. PCA and Factor Analysis, both reduced to k dimensions
    pca = PCA(n_components=k).fit(X)
    fa = FactorAnalysis(n_components=k, random_state=0).fit(X)

    pca_scores = pca.transform(X)
    fa_scores = fa.transform(X)
    pca_loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
    fa_loadings = fa.components_.T

    print(f'PCA loadings (k={k})')
    display(pd.DataFrame(pca_loadings, index=columns, columns=[f'PC{i + 1}' for i in range(k)]))
    print(f'Factor Analysis loadings (k={k})')
    display(pd.DataFrame(fa_loadings, index=columns, columns=[f'Factor{i + 1}' for i in range(k)]))

    # 4. Biplots: player scores (coloured by group_col) with feature loading vectors overlaid,
    # one grid per method, showing every pairwise combination of the k retained dimensions
    dim_pairs = [(i, j) for i in range(k) for j in range(i + 1, k)] if k > 1 else [(0, None)]
    biplot_cols_per_row = min(3, len(dim_pairs))
    n_rows = (len(dim_pairs) + biplot_cols_per_row - 1) // biplot_cols_per_row

    for scores, loadings, title in [
        (pca_scores, pca_loadings, 'PCA'),
        (fa_scores, fa_loadings, 'Factor Analysis'),
    ]:
        fig, axes = plt.subplots(n_rows, biplot_cols_per_row, figsize=(6 * biplot_cols_per_row, 6 * n_rows), squeeze=False)
        for ax, (dx, dy) in zip(axes.flat, dim_pairs):
            y_scores = scores[:, dy] if dy is not None else np.zeros(len(scores))
            for grp in palette:
                mask = (plot_df[group_col] == grp).values
                ax.scatter(scores[mask, dx], y_scores[mask], color=palette[grp], alpha=0.5, s=20, label=grp)

            y_loadings = loadings[:, dy] if dy is not None else np.zeros(len(loadings))
            # scale x/y independently - PCA dims have sharply decreasing variance, so a shared
            # scale (based on dx) over-inflates arrows on the smaller-variance axis and squishes the points
            scale_x = np.abs(scores[:, dx]).max() / np.abs(loadings[:, dx]).max() * 0.8
            scale_y = np.abs(y_scores).max() / np.abs(y_loadings).max() * 0.8 if dy is not None else scale_x
            for i, col_name in enumerate(columns):
                x, y = loadings[i, dx] * scale_x, y_loadings[i] * scale_y
                ax.annotate('', xy=(x, y), xytext=(0, 0), arrowprops={'arrowstyle': '->', 'color': 'black'})
                ax.text(x * 1.15, y * 1.15, col_name, fontsize=8, ha='center', va='center')

            ax.axhline(0, color='grey', linewidth=0.5)
            ax.axvline(0, color='grey', linewidth=0.5)
            ax.set_xlabel(f'Dim {dx + 1}')
            ax.set_ylabel(f'Dim {dy + 1}' if dy is not None else '')
            dy_label = dy + 1 if dy is not None else '-'
            ax.set_title(f'Dim {dx + 1} vs Dim {dy_label}', fontsize=12, fontweight='bold')
        for ax in axes.flat[len(dim_pairs):]:
            ax.set_visible(False)
        axes.flat[0].legend(title=group_col)
        fig.suptitle(f'{title} Biplots', fontsize=15, fontweight='bold')
        plt.tight_layout()
        plt.show()

    return scaler, {'pca': pca, 'fa': fa}


def add_reduced_dimensions(df, target_df, columns, method='pca', k=None, col_names=None, fitted_scaler=None, fitted_model=None, signs=None):
    """
    Fits PCA or Factor Analysis on the specified columns of df (or uses pre-fitted models),
    transforms the data, and adds the resulting scores as new columns in target_df,
    aligned by index.

    Parameters:
    -----------
    df : pandas.DataFrame
        The source DataFrame containing the raw numeric columns.
    target_df : pandas.DataFrame
        The target DataFrame to which the reduced dimension columns will be added.
    columns : list-like
        The list of columns to perform dimensionality reduction on.
    method : str, default 'pca'
        The method to use ('pca' or 'fa'). Ignored if fitted_model is provided.
    k : int, optional
        The number of components/factors. Ignored if fitted_model is provided.
        If None and fitted_model is None, it is automatically determined using the
        elbow - 1 heuristic (consistent with explore_dimensionality_reduction).
    col_names : list of str, optional
        The names for the new columns in target_df. Must match the length of k.
        If None, they will default to PC1, PC2... or Factor1, Factor2...
    fitted_scaler : sklearn.preprocessing.StandardScaler, optional
        A pre-fitted StandardScaler. If provided, fitted_model must also be provided.
    fitted_model : sklearn.decomposition.PCA or sklearn.decomposition.FactorAnalysis, optional
        A pre-fitted PCA or FactorAnalysis model. If provided, fitted_scaler must also be provided.
    signs : list of str or int, optional
        Assigns the sign multiplier of each component/factor scores to guarantee semantic directionality
        (e.g., ['+', '-'] or [1, -1]). Must match the length of k.
    
    Returns:
    --------
    pandas.DataFrame
        A copy of target_df with the new reduced dimension columns added.
    """
    columns = list(columns)
    valid_data = df[columns].dropna()

    if fitted_scaler is not None and fitted_model is not None:
        # Use pre-fitted models (prevents sign flip / row mismatches)
        X = fitted_scaler.transform(valid_data)
        scores = fitted_model.transform(X)
        k = scores.shape[1]
    else:
        # Fit from scratch
        method = method.lower()
        if method not in ['pca', 'fa']:
            raise ValueError("method must be either 'pca' or 'fa'")

        X = StandardScaler().fit_transform(valid_data)

        # Calculate k via elbow heuristic if not provided
        eigenvalues = PCA().fit(X).explained_variance_
        comps = np.arange(1, len(eigenvalues) + 1)

        x_norm = (comps - comps.min()) / (comps.max() - comps.min())
        y_norm = (eigenvalues - eigenvalues.min()) / (eigenvalues.max() - eigenvalues.min())
        line_vec = np.array([x_norm[-1] - x_norm[0], y_norm[-1] - y_norm[0]])
        line_vec /= np.linalg.norm(line_vec)
        vec_from_first = np.stack([x_norm - x_norm[0], y_norm - y_norm[0]], axis=1)
        vec_parallel = np.outer(vec_from_first @ line_vec, line_vec)
        dist_from_line = np.linalg.norm(vec_from_first - vec_parallel, axis=1)
        elbow = int(np.argmax(dist_from_line)) + 1
        
        if k is None:
            k = max(1, elbow - 1)
        else:
            k = int(k)

        if method == 'pca':
            fitted_model = PCA(n_components=k).fit(X)
        else:
            fitted_model = FactorAnalysis(n_components=k, random_state=0).fit(X)

        scores = fitted_model.transform(X)

    if signs is not None:
        if len(signs) != k:
            raise ValueError(f"Length of signs ({len(signs)}) must match k ({k})")
        
        parsed_signs = []
        for i, s in enumerate(signs):
            if s in [1, '+', '1', '+1']:
                parsed_signs.append(1)
            elif s in [-1, '-', '-1']:
                parsed_signs.append(-1)
            elif isinstance(s, str):
                # Check if it's a feature name or prefixed with '-'
                is_negative = s.startswith('-')
                feature_name = s[1:] if is_negative else s
                feature_name = feature_name.strip()
                
                if feature_name in columns:
                    col_idx = columns.index(feature_name)
                    # Inspect the loading of this feature on component i
                    # fitted_model.components_ has shape (n_components, n_features)
                    loading_val = fitted_model.components_[i, col_idx]
                    
                    # Align component sign so that the loading matches requested sign
                    if loading_val >= 0:
                        multiplier = -1 if is_negative else 1
                    else:
                        multiplier = 1 if is_negative else -1
                    parsed_signs.append(multiplier)
                else:
                    raise ValueError(f"Invalid sign indicator or feature name '{s}'. Feature must be in columns: {columns}")
            else:
                raise ValueError(f"Invalid sign indicator '{s}'. Must be '+', '-', 1, -1, or a column name.")
        
        for i in range(k):
            scores[:, i] *= parsed_signs[i]

    if col_names is None:
        if isinstance(fitted_model, PCA):
            col_names = [f'PC{i + 1}' for i in range(k)]
        else:
            col_names = [f'Factor{i + 1}' for i in range(k)]
    else:
        if len(col_names) != k:
            raise ValueError(f"Length of col_names ({len(col_names)}) must match k ({k})")

    scores_df = pd.DataFrame(scores, index=valid_data.index, columns=col_names)

    target_df = target_df.copy()
    for col in col_names:
        target_df[col] = scores_df[col]

    return target_df
