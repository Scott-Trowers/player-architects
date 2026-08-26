import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display
from matplotlib.lines import Line2D

from scripts.constants import PRIMARY_POS_ORDER


def explore_outliers(df, player_identifiers, columns, primary_pos=None, id_col='player_identifier',
                      name_col='Player', group_col='Primary_Pos', radar_cols_per_row=4,
                      highlight_color='teal', other_color='grey'):
    columns = list(columns)
    positions = ([primary_pos] if isinstance(primary_pos, str) else list(primary_pos)) if primary_pos is not None else None
    plot_df = df[df[group_col].isin(positions)].copy() if positions is not None else df.copy()
    plot_df = plot_df.dropna(subset=columns)

    highlight_mask = plot_df[id_col].isin(player_identifiers)
    missing_ids = set(player_identifiers) - set(plot_df.loc[highlight_mask, id_col])
    if missing_ids:
        print(f"Note: {len(missing_ids)} requested player_identifier(s) not present after filtering: {sorted(missing_ids)}")

    # 1. Player/team/playing-time info alongside the metrics of interest, for the selected players
    player_info_cols = ['player_identifier', 'Player', 'Nation', 'Primary_Pos', 'Age', 'Born', 'Num_Pos']
    team_info_cols = ['Squad', 'Comp']
    matches_played_cols = ['MP', 'Starts', 'Min', '90s']
    info_cols = list(dict.fromkeys(player_info_cols + team_info_cols + matches_played_cols + columns))
    info_cols = [c for c in info_cols if c in plot_df.columns]
    display(plot_df.loc[highlight_mask, info_cols].reset_index(drop=True))

    # 2. Scaled parallel coordinates, highlighted players drawn on top of the rest
    col_range = (plot_df[columns].max() - plot_df[columns].min()).replace(0, 1)
    scaled = (plot_df[columns] - plot_df[columns].min()) / col_range

    fig, ax = plt.subplots(figsize=(max(12, len(columns) * 1.2), 6))
    x = list(range(len(columns)))
    for _, row in scaled[~highlight_mask].iterrows():
        ax.plot(x, row[columns], color=other_color, alpha=0.25, linewidth=1)
    for _, row in scaled[highlight_mask].iterrows():
        ax.plot(x, row[columns], color=highlight_color, alpha=0.9, linewidth=2.2)
    ax.set_xticks(x)
    ax.set_xticklabels(columns, rotation=45, ha='right')
    title_suffix = f' ({", ".join(positions)})' if positions else ''
    ax.set_title(f'Parallel Coordinates{title_suffix} - Highlighted Players', fontsize=14, fontweight='bold')
    ax.legend(handles=[
        Line2D([0], [0], color=other_color, lw=1, alpha=0.5, label='Other players'),
        Line2D([0], [0], color=highlight_color, lw=2.2, label='Highlighted players'),
    ], loc='upper right')
    plt.tight_layout()
    plt.show()

    # 3. Full scatterplot matrix, highlighted players drawn on top of the rest
    labeled_df = plot_df.copy()
    labeled_df['Highlight'] = np.where(highlight_mask, 'Highlighted', 'Other')

    g = sns.PairGrid(labeled_df, vars=columns, hue='Highlight', hue_order=['Other', 'Highlighted'],
                      palette={'Other': other_color, 'Highlighted': highlight_color}, diag_sharey=False)
    g.map_diag(sns.histplot)
    g.map_offdiag(sns.scatterplot, alpha=0.7, s=25, edgecolor='none')
    g.add_legend(title='')
    plt.show()

    # 4. Radar grid: average panel (overall + per-position) first, then one panel per highlighted player
    col_min = plot_df[columns].min()
    col_max = plot_df[columns].max()
    col_span = (col_max - col_min).replace(0, 1)

    angles = np.linspace(0, 2 * np.pi, len(columns), endpoint=False).tolist()
    angles += angles[:1]

    avg_positions = [p for p in PRIMARY_POS_ORDER if p != 'GK' and p in df[group_col].unique()]
    avg_palette = dict(zip(avg_positions, sns.color_palette('tab10', n_colors=len(avg_positions))))

    average_panel = [('Overall', df[columns].mean(), other_color)]
    average_panel += [(pos, df.loc[df[group_col] == pos, columns].mean(), avg_palette[pos]) for pos in avg_positions]

    panels = [average_panel]
    panels += [[(row[name_col], row[columns], highlight_color)] for _, row in plot_df[highlight_mask].iterrows()]

    n_rows = (len(panels) + radar_cols_per_row - 1) // radar_cols_per_row
    fig, axes = plt.subplots(n_rows, radar_cols_per_row, figsize=(4 * radar_cols_per_row, 4 * n_rows),
                              subplot_kw=dict(polar=True), squeeze=False)

    for ax, series_list in zip(axes.flat, panels):
        for label, raw_values, color in series_list:
            normalized = ((raw_values - col_min) / col_span).tolist()
            normalized += normalized[:1]
            raw_list = raw_values.tolist()

            ax.plot(angles, normalized, color=color, linewidth=2, label=label)
            ax.fill(angles, normalized, color=color, alpha=0.15 if len(series_list) > 1 else 0.25)

            if len(series_list) == 1:
                for angle, val, raw in zip(angles[:-1], normalized[:-1], raw_list):
                    ax.text(angle, val + 0.05, f'{raw:.2f}', fontsize=7, ha='center', va='center', color=color)

        ax.set_ylim(0, 1)
        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(columns, fontsize=8)

        for angle, col in zip(angles[:-1], columns):
            ax.text(angle, -0.08, f'{col_min[col]:.2f}', fontsize=7, ha='center', va='center', color='#898781')
            ax.text(angle, 1.08, f'{col_max[col]:.2f}', fontsize=7, ha='center', va='center', color='#898781')

        if len(series_list) > 1:
            ax.set_title('Average', fontsize=11, pad=15)
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=7)
        else:
            ax.set_title(str(series_list[0][0]), fontsize=11, pad=15)

    for ax in axes.flat[len(panels):]:
        ax.set_visible(False)
    plt.tight_layout()
    plt.show()
