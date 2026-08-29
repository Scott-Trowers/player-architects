import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from IPython.display import display
from pandas.plotting import parallel_coordinates
from scipy import stats

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


def explore_column_group(
    df,
    columns,
    group_col='Primary_Pos',
    player_col='Player',
    hist_cols_per_row=4,
    bar_cols_per_row=4,
    lollipop_cols_per_row=4,
    palette=None,
    high_dimensionality=False,
):
    """Run the EDA suite on a metric group.

    If high_dimensionality=True, skips memory/visual-heavy plots (lollipop
    charts, scatterplot matrix, and group bar charts).
    """
    columns = list(columns)
    plot_df = df[columns + [group_col]].dropna()

    if palette is None:
        groups = sorted(plot_df[group_col].unique())
        palette = dict(
            zip(groups, sns.color_palette('tab10', n_colors=len(groups)))
        )

    present_groups = plot_df[group_col].unique()
    group_order = [p for p in PRIMARY_POS_ORDER if p in present_groups]
    group_order += [p for p in present_groups if p not in PRIMARY_POS_ORDER]

    # 1. Descriptive statistics
    summary = df[columns].describe()
    summary.loc['skew'] = df[columns].skew()
    summary.loc['kurtosis'] = df[columns].kurt()
    display(summary)

    # 2. Histogram + KDE with integrated boxplot
    chunks = [
        columns[i : i + hist_cols_per_row]
        for i in range(0, len(columns), hist_cols_per_row)
    ]
    for chunk in chunks:
        fig, axes = plt.subplots(
            2,
            hist_cols_per_row,
            figsize=(hist_cols_per_row * 5.5, 5),
            sharex='col',
            gridspec_kw={'height_ratios': (0.95, 0.05)},
            squeeze=False,
        )
        for i in range(hist_cols_per_row):
            ax_hist, ax_box = axes[0, i], axes[1, i]
            if i < len(chunk):
                col = chunk[i]
                sns.histplot(data=df, x=col, kde=True, color='teal', ax=ax_hist)
                ax_hist.set_title(
                    f'Distribution of {col}', fontsize=14, fontweight='bold'
                )
                ax_hist.set_ylabel('Density', fontsize=11)
                ax_hist.tick_params(labelbottom=False)
                sns.despine(ax=ax_hist, top=True, right=True, bottom=True)

                sns.boxplot(
                    data=df,
                    x=col,
                    color='#3F51B5',
                    width=0.3,
                    ax=ax_box,
                    showmeans=True,
                    meanprops={
                        'marker': '+',
                        'markeredgecolor': 'white',
                        'markerfacecolor': 'white',
                        'markersize': 8,
                    },
                    medianprops={'color': 'white', 'linewidth': 2},
                    fliersize=2,
                )
                ax_box.set_xlabel(col, fontsize=12)
                ax_box.yaxis.set_visible(False)
                sns.despine(
                    ax=ax_box, left=True, top=True, right=True, bottom=False
                )
            else:
                ax_hist.xaxis.set_visible(False)
                ax_hist.yaxis.set_visible(False)
                ax_hist.grid(False)
                for spine in ax_hist.spines.values():
                    spine.set_color('#e0e0e0')
                    spine.set_linestyle('--')
                    spine.set_visible(True)

                ax_box.xaxis.set_visible(False)
                ax_box.yaxis.set_visible(False)
                ax_box.grid(False)
                for spine in ax_box.spines.values():
                    spine.set_color('#e0e0e0')
                    spine.set_linestyle('--')
                    spine.set_visible(True)
        fig.subplots_adjust(hspace=0.0)
        plt.show()

    # 3. Highest and lowest 5 players (lollipop charts)
    if not high_dimensionality:
        chunks = [
            columns[i : i + lollipop_cols_per_row]
            for i in range(0, len(columns), lollipop_cols_per_row)
        ]
        for chunk in chunks:
            fig, axes = plt.subplots(
                1,
                lollipop_cols_per_row,
                figsize=(lollipop_cols_per_row * 5.5, 6),
                squeeze=False,
            )
            for i in range(lollipop_cols_per_row):
                ax = axes[0, i]
                if i < len(chunk):
                    col = chunk[i]
                    highest = df[[player_col, col, group_col]].nlargest(5, col)
                    lowest = df[[player_col, col, group_col]].nsmallest(5, col)
                    labels = (
                        highest[player_col].tolist()
                        + ['']
                        + lowest[player_col].tolist()
                    )
                    values = np.array(
                        highest[col].tolist() + [np.nan] + lowest[col].tolist(),
                        dtype=float,
                    )
                    group_colors = (
                        highest[group_col].map(palette).tolist()
                        + [None]
                        + lowest[group_col].map(palette).tolist()
                    )
                    colors = np.array(
                        ['gray' if c is None else c for c in group_colors],
                        dtype=object,
                    )
                    y_pos = np.arange(len(labels))[::-1]
                    valid = ~np.isnan(values)

                    ax.hlines(
                        y_pos[valid],
                        xmin=0,
                        xmax=values[valid],
                        color=colors[valid],
                        linewidth=2,
                    )
                    ax.scatter(
                        values[valid],
                        y_pos[valid],
                        color=colors[valid],
                        s=60,
                        zorder=3,
                    )
                    for y, v in zip(y_pos[valid], values[valid]):
                        ax.text(
                            v,
                            y,
                            f' {v:.2f}',
                            va='center',
                            ha='left' if v >= 0 else 'right',
                            fontsize=9,
                        )

                    ax.axvline(0, color='black', linewidth=0.8)
                    ax.set_yticks(y_pos)
                    ax.set_yticklabels(labels, fontsize=9)
                    ax.set_title(
                        f'Highest/Lowest 5 - {col}',
                        fontsize=12,
                        fontweight='bold',
                    )
                    ax.margins(x=0.2)
                    sns.despine(ax=ax, left=True)
                else:
                    ax.xaxis.set_visible(False)
                    ax.yaxis.set_visible(False)
                    ax.grid(False)
                    for spine in ax.spines.values():
                        spine.set_color('#e0e0e0')
                        spine.set_linestyle('--')
                        spine.set_visible(True)
            handles = [
                plt.Line2D(
                    [0],
                    [0],
                    marker='o',
                    linestyle='',
                    color=palette[grp],
                    markersize=8,
                    label=grp,
                )
                for grp in group_order
            ]
            fig.legend(
                handles=handles,
                title=group_col,
                loc='upper center',
                bbox_to_anchor=(0.5, 1.05),
                ncol=len(group_order),
            )
            plt.tight_layout()
            plt.show()

    # 4. Correlation matrix
    plt.figure(figsize=(max(8, len(columns) * 0.8), max(6, len(columns) * 0.7)))
    corr = df[columns].corr()
    sns.heatmap(
        corr,
        annot=len(columns) <= 15,
        cmap='coolwarm',
        fmt='.2f',
        vmin=-1,
        vmax=1,
        square=True,
    )
    plt.title('Correlation Matrix', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()

    # 5. Scatterplot matrix
    if not high_dimensionality:
        g = sns.PairGrid(
            plot_df,
            vars=columns,
            hue=group_col,
            palette=palette,
            diag_sharey=False,
        )
        g.map_diag(sns.kdeplot, warn_singular=False)
        g.map_lower(sns.scatterplot, alpha=0.3, s=20, edgecolor='none')
        g.map_upper(_annotate_corr)
        g.add_legend(title=group_col)
        plt.show()

    # 6. Scaled parallel coordinates plot
    col_range = (plot_df[columns].max() - plot_df[columns].min()).replace(0, 1)
    scaled = (plot_df[columns] - plot_df[columns].min()) / col_range
    scaled[group_col] = plot_df[group_col].values

    fig, ax = plt.subplots(figsize=(max(12, len(columns) * 1.2), 6))
    parallel_coordinates(
        scaled,
        group_col,
        color=[palette[grp] for grp in sorted(palette)],
        ax=ax,
        alpha=0.25,
    )
    ax.set_title(
        f'Parallel Coordinates (scaled) by {group_col}',
        fontsize=14,
        fontweight='bold',
    )
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    # 7. Grid of bar charts: mean per group
    if not high_dimensionality:
        group_means = plot_df.groupby(group_col)[columns].mean().loc[
            group_order
        ]
        n_rows = (len(columns) + bar_cols_per_row - 1) // bar_cols_per_row
        fig, axes = plt.subplots(
            n_rows,
            bar_cols_per_row,
            figsize=(4 * bar_cols_per_row, 4 * n_rows),
            squeeze=False,
        )
        for ax, col in zip(axes.flat, columns):
            ax.bar(
                group_means.index,
                group_means[col],
                color=[palette[p] for p in group_means.index],
            )
            ax.set_title(col)
            ax.tick_params(axis='x', rotation=45)
        for ax in axes.flat[len(columns) :]:
            ax.set_visible(False)
        plt.tight_layout()
        plt.show()

def explore_high_correlations(
    df,
    columns,
    group_col="Primary_Pos",
    threshold=0.95,
    cols_per_row=3,
    palette=None,
):
    """Identifies feature pairs with absolute Pearson correlation above threshold

    and renders a grid of scatterplots colored by group_col.
    """
    columns = list(columns)
    plot_df = df[columns + [group_col]].dropna()

    # 1. Compute Pearson correlation matrix
    corr_matrix = plot_df[columns].corr()

    # 2. Identify unique pairs above the correlation threshold
    pairs = []
    for i in range(len(columns)):
        for j in range(i + 1, len(columns)):
            c1, c2 = columns[i], columns[j]
            r = corr_matrix.loc[c1, c2]
            if abs(r) >= threshold:
                pairs.append((c1, c2, r))

    if not pairs:
        print(
            f"No column pairs found with |r| >= {threshold:.2f} across"
            f" {len(columns)} metrics."
        )
        return

    # Sort pairs by absolute correlation magnitude (highest first)
    pairs.sort(key=lambda x: abs(x[2]), reverse=True)

    # 3. Handle color palette
    if palette is None:
        groups = sorted(plot_df[group_col].unique())
        palette = dict(
            zip(groups, sns.color_palette("tab10", n_colors=len(groups)))
        )

    # 4. Set up subplot grid
    n_pairs = len(pairs)
    n_cols = min(cols_per_row, n_pairs)
    n_rows = (n_pairs + n_cols - 1) // n_cols

    _fig, axes = plt.subplots(
        n_rows,
        n_cols,
        figsize=(5 * n_cols, 4.5 * n_rows),
        squeeze=False,
    )

    # 5. Plot scatterplots
    for idx, (c1, c2, r) in enumerate(pairs):
        row_idx, col_idx = divmod(idx, n_cols)
        ax = axes[row_idx, col_idx]

        sns.scatterplot(
            data=plot_df,
            x=c1,
            y=c2,
            hue=group_col,
            palette=palette,
            alpha=0.7,
            s=40,
            ax=ax,
        )

        ax.set_title(
            f"{c1}\nvs {c2}\n(r = {r:.3f})", fontsize=10, fontweight="bold"
        )
        ax.set_xlabel(c1, fontsize=9)
        ax.set_ylabel(c2, fontsize=9)
        sns.despine(ax=ax)

        # Place legend outside on the top right cell to prevent duplication
        if idx == 0:
            ax.legend(
                title=group_col,
                bbox_to_anchor=(1.05, 1),
                loc="upper left",
                frameon=False,
            )
        else:
            ax.get_legend().remove()

    # 6. Hide leftover unused subplot axes
    for idx in range(n_pairs, n_rows * n_cols):
        row_idx, col_idx = divmod(idx, n_cols)
        axes[row_idx, col_idx].set_visible(False)

    plt.tight_layout()
    plt.show()
