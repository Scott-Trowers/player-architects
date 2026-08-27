import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import seaborn as sns
from IPython.display import display
from pandas.plotting import parallel_coordinates

from scripts.constants import PRIMARY_POS_ORDER


def _annotate_corr(x, y, **kwargs):
    """Write a Pearson r for the current hue group into a PairGrid upper-triangle cell."""
    ax = plt.gca()
    color = kwargs.get('color', 'black')
    count = getattr(ax, '_corr_count', 0)
    r, _ = stats.pearsonr(x, y)
    ax.annotate(f'r = {r:.2f}', xy=(0.5, 0.85 - count * 0.18), xycoords=ax.transAxes,
                ha='center', va='center', fontsize=10, color=color)
    ax.set_xticks([])
    ax.set_yticks([])
    ax._corr_count = count + 1


def explore_column_group(df, columns, group_col='Primary_Pos', player_col='Player', hist_cols_per_row=4, bar_cols_per_row=4, lollipop_cols_per_row=4, palette=None):
    """Run the standard EDA suite (stats, distributions, correlation, pairwise, parallel, group means) on a metric group."""
    columns = list(columns)
    # rows need a valid group_col for the three group-coloured plots; stats/hist/corr use the full df
    plot_df = df[columns + [group_col]].dropna()

    if palette is None:
        groups = sorted(plot_df[group_col].unique())
        palette = dict(zip(groups, sns.color_palette('tab10', n_colors=len(groups))))

    # 1. Descriptive statistics, including skew and kurtosis
    summary = df[columns].describe()
    summary.loc['skew'] = df[columns].skew()
    summary.loc['kurtosis'] = df[columns].kurt()
    display(summary)

    # 2. Histogram + KDE with an integrated boxplot, chunked into rows
    chunks = [columns[i:i + hist_cols_per_row] for i in range(0, len(columns), hist_cols_per_row)]
    for chunk in chunks:
        n_cols = len(chunk)
        fig, axes = plt.subplots(
            2, n_cols, figsize=(n_cols * 5.5, 10), sharex='col',
            gridspec_kw={'height_ratios': (0.95, 0.05)}, squeeze=False,
        )
        for i, col in enumerate(chunk):
            ax_hist, ax_box = axes[0, i], axes[1, i]
            sns.histplot(data=df, x=col, kde=True, color='teal', ax=ax_hist)
            ax_hist.set_title(f'Distribution of {col}', fontsize=14, fontweight='bold')
            ax_hist.set_ylabel('Density', fontsize=11)
            ax_hist.tick_params(labelbottom=False)
            sns.despine(ax=ax_hist, top=True, right=True, bottom=True)

            sns.boxplot(
                data=df, x=col, color='#3F51B5', width=0.3, ax=ax_box, showmeans=True,
                meanprops={'marker': '+', 'markeredgecolor': 'white', 'markerfacecolor': 'white', 'markersize': 8},
                medianprops={'color': 'white', 'linewidth': 2}, fliersize=2,
            )
            ax_box.set_xlabel(col, fontsize=12)
            ax_box.yaxis.set_visible(False)
            sns.despine(ax=ax_box, left=True, top=True, right=True, bottom=False)
        fig.subplots_adjust(hspace=0.0)
        plt.show()

    # 3. Highest and lowest 5 players for each metric, as annotated lollipop charts
    chunks = [columns[i:i + lollipop_cols_per_row] for i in range(0, len(columns), lollipop_cols_per_row)]
    for chunk in chunks:
        fig, axes = plt.subplots(1, len(chunk), figsize=(5.5 * len(chunk), 6), squeeze=False)
        for ax, col in zip(axes[0], chunk):
            highest = df[[player_col, col]].nlargest(5, col)
            lowest = df[[player_col, col]].nsmallest(5, col)
            labels = highest[player_col].tolist() + [''] + lowest[player_col].tolist()
            values = np.array(highest[col].tolist() + [np.nan] + lowest[col].tolist(), dtype=float)
            colors = np.array(['teal'] * len(highest) + ['white'] + ['#C44E52'] * len(lowest), dtype=object)
            y_pos = np.arange(len(labels))[::-1]
            valid = ~np.isnan(values)

            ax.hlines(y_pos[valid], xmin=0, xmax=values[valid], color=colors[valid], linewidth=2)
            ax.scatter(values[valid], y_pos[valid], color=colors[valid], s=60, zorder=3)
            for y, v in zip(y_pos[valid], values[valid]):
                ax.text(v, y, f' {v:.2f}', va='center', ha='left' if v >= 0 else 'right', fontsize=9)

            ax.axvline(0, color='black', linewidth=0.8)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(labels, fontsize=9)
            ax.set_title(f'Highest/Lowest 5 - {col}', fontsize=12, fontweight='bold')
            ax.margins(x=0.2)
            sns.despine(ax=ax, left=True)
        for ax in axes[0][len(chunk):]:
            ax.set_visible(False)
        plt.tight_layout()
        plt.show()

    # 4. Correlation matrix
    plt.figure(figsize=(max(8, len(columns) * 0.8), max(6, len(columns) * 0.7)))
    corr = df[columns].corr()
    sns.heatmap(corr, annot=len(columns) <= 15, cmap='coolwarm', fmt='.2f', vmin=-1, vmax=1, square=True)
    plt.title('Correlation Matrix', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()

    # 5. Scatterplot matrix, coloured by group_col
    g = sns.PairGrid(plot_df, vars=columns, hue=group_col, palette=palette, diag_sharey=False)
    g.map_diag(sns.kdeplot, warn_singular=False)
    g.map_lower(sns.scatterplot, alpha=0.3, s=20, edgecolor='none')
    g.map_upper(_annotate_corr)
    g.add_legend(title=group_col)
    plt.show()

    # 6. Scaled parallel coordinates plot, coloured by group_col
    col_range = (plot_df[columns].max() - plot_df[columns].min()).replace(0, 1)
    scaled = (plot_df[columns] - plot_df[columns].min()) / col_range
    scaled[group_col] = plot_df[group_col].values

    fig, ax = plt.subplots(figsize=(max(12, len(columns) * 1.2), 6))
    parallel_coordinates(scaled, group_col, color=[palette[grp] for grp in sorted(palette)], ax=ax, alpha=0.25)
    ax.set_title(f'Parallel Coordinates (scaled) by {group_col}', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    # 7. Grid of bar charts: mean of each column, per group
    group_means = plot_df.groupby(group_col)[columns].mean()
    group_order = [p for p in PRIMARY_POS_ORDER if p in group_means.index]
    group_order += [p for p in group_means.index if p not in PRIMARY_POS_ORDER]
    group_means = group_means.loc[group_order]
    n_rows = (len(columns) + bar_cols_per_row - 1) // bar_cols_per_row
    fig, axes = plt.subplots(n_rows, bar_cols_per_row, figsize=(4 * bar_cols_per_row, 4 * n_rows), squeeze=False)
    for ax, col in zip(axes.flat, columns):
        ax.bar(group_means.index, group_means[col], color=[palette[p] for p in group_means.index])
        ax.set_title(col)
        ax.tick_params(axis='x', rotation=45)
    for ax in axes.flat[len(columns):]:
        ax.set_visible(False)
    plt.tight_layout()
    plt.show()

    """
    # 8. Circular bar (radar) chart per group, plus an overall "All Players" panel: mean of each
    # column scaled by that panel's own max so every spoke starts at a true zero. bars are drawn as
    # thin spokes rather than wide wedges, so there's no filled area to misjudge and the radius can
    # stay a plain linear mean/max scale. annotations show the real (unscaled) max and mean.
    group_max = plot_df.groupby(group_col)[columns].max().loc[group_order]
    scaled_means = group_means[columns] / group_max[columns]

    panels = ['All Players'] + group_order
    panel_means = dict(group_means[columns].T.items())
    panel_means['All Players'] = plot_df[columns].mean()
    panel_max = dict(group_max[columns].T.items())
    panel_max['All Players'] = plot_df[columns].max()
    panel_scaled = dict(scaled_means[columns].T.items())
    panel_scaled['All Players'] = panel_means['All Players'] / panel_max['All Players']
    panel_color = {**palette, 'All Players': 'teal'}

    angles = np.linspace(0, 2 * np.pi, len(columns), endpoint=False)
    n_cols_grid = min(4, len(panels))
    n_rows_grid = (len(panels) + n_cols_grid - 1) // n_cols_grid
    fig, axes = plt.subplots(
        n_rows_grid, n_cols_grid, figsize=(5 * n_cols_grid, 5 * n_rows_grid),
        squeeze=False, subplot_kw={'projection': 'polar'},
    )
    for ax, panel in zip(axes.flat, panels):
        scaled_values = panel_scaled[panel][columns].values
        raw_values = panel_means[panel][columns].values
        max_values = panel_max[panel][columns].values
        ax.bar(angles, scaled_values, width=0.65, color=panel_color[panel], alpha=0.9)
        for angle, scaled_v, raw_v in zip(angles, scaled_values, raw_values):
            ax.text(angle, scaled_v + 0.08, f'{raw_v:.2g}', ha='center', va='center', fontsize=7)
        ax.set_xticks(angles)
        ax.set_xticklabels([f'{col}\n(max: {max_v:.2g})' for 
        col, max_v in zip(columns, max_values)], fontsize=7)
        ax.set_ylim(0, 1.2)
        ax.set_yticklabels([])  # radial ticks are a normalised scale, not real units - hide them
        ax.set_title(panel, fontsize=12, fontweight='bold', pad=20)
    for ax in axes.flat[len(panels):]:
        ax.set_visible(False)
    plt.tight_layout()
    plt.show()
    """
