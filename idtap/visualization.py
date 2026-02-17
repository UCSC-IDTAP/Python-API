"""Matplotlib visualization functions for IDTAP musical transcription data.

Provides melodic contour plots, pitch prevalence heatmaps, and pitch pattern
visualizations that mirror the D3.js-based analysis views in the IDTAP web app.
"""

from __future__ import annotations

import math
import numpy as np
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

from .classes.trajectory import Trajectory
from .classes.pitch import Pitch
from .classes.automation import get_starts
from .analysis import (
    durations_of_pitch_onsets,
    pattern_counter,
    segment_by_duration,
    chroma_seq_to_condensed_pitch_nums,
)

if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from matplotlib.axes import Axes
    from .classes.piece import Piece
    from .classes.raga import Raga


# 12-colour chroma scheme (one per semitone within an octave)
CHROMA_COLORS = [
    '#e6194b', '#3cb44b', '#ffe119', '#4363d8',
    '#f58231', '#911eb4', '#42d4f4', '#f032e6',
    '#bfef45', '#fabed4', '#469990', '#dcbeff',
]


def plot_melodic_contour(
    trajectories: List[Trajectory],
    raga: Optional['Raga'] = None,
    ax: Optional['Axes'] = None,
    figsize: Tuple[float, float] = (12, 4),
    num_samples: int = 200,
    line_color: str = 'black',
    line_width: float = 1.0,
    ref_line_alpha: float = 0.3,
    title: Optional[str] = None,
) -> 'Figure':
    """Plot a melodic contour from a sequence of trajectories.

    Mirrors the SegmentDisplay component from the IDTAP web app.  For each
    non-silent trajectory, samples ``traj.compute(x, log_scale=True)`` and
    plots the resulting log₂-frequency curve over absolute time.

    Args:
        trajectories: Sequence of trajectories to plot.
        raga: Optional Raga for pitch reference lines and Sargam labels.
        ax: Existing matplotlib Axes to draw on.  If *None*, a new Figure
            and Axes are created.
        figsize: Figure size if creating new Figure.
        num_samples: Number of sample points per trajectory.
        line_color: Colour of the contour line.
        line_width: Width of the contour line.
        ref_line_alpha: Alpha of raga reference lines.
        title: Optional plot title.

    Returns:
        The matplotlib Figure containing the plot.
    """
    import matplotlib.pyplot as plt

    own_fig = ax is None
    if own_fig:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure  # type: ignore[union-attr]

    traj_durs = [t.dur_tot for t in trajectories]
    starts = get_starts(traj_durs)
    total_dur = sum(traj_durs)

    for i, traj in enumerate(trajectories):
        if traj.id == 12:
            continue  # skip silence
        t0 = starts[i]
        xs = np.linspace(0, 1, num_samples, endpoint=False)
        times = t0 + xs * traj.dur_tot
        log_freqs = [traj.compute(float(x), log_scale=True) for x in xs]
        ax.plot(times, log_freqs, color=line_color, linewidth=line_width)  # type: ignore[union-attr]

    # Raga reference lines
    if raga is not None:
        # Determine y range from plotted data
        y_min, y_max = ax.get_ylim()  # type: ignore[union-attr]
        low_hz = 2 ** y_min
        high_hz = 2 ** y_max
        ref_pitches = raga.get_pitches(low=low_hz, high=high_hz)
        for p in ref_pitches:
            log_f = math.log2(p.frequency)
            ax.axhline(  # type: ignore[union-attr]
                y=log_f,
                color='grey',
                linestyle='--',
                linewidth=0.5,
                alpha=ref_line_alpha,
            )
            label = p.sargam_letter
            ax.text(  # type: ignore[union-attr]
                0, log_f, f' {label}',
                va='center', ha='left',
                fontsize=7, color='grey', alpha=ref_line_alpha + 0.2,
            )

    ax.set_xlabel('Time (s)')  # type: ignore[union-attr]
    ax.set_ylabel('log₂(frequency)')  # type: ignore[union-attr]
    if total_dur > 0:
        ax.set_xlim(0, total_dur)  # type: ignore[union-attr]
    if title:
        ax.set_title(title)  # type: ignore[union-attr]

    if own_fig:
        fig.tight_layout()

    return fig


def plot_pitch_prevalence(
    piece: 'Piece',
    segmentation: str = 'section',
    output_type: str = 'pitchNumber',
    pitch_representation: str = 'pitch_onsets',
    segment_duration: float = 10,
    inst: int = 0,
    ax: Optional['Axes'] = None,
    figsize: Tuple[float, float] = (10, 6),
    cmap: str = 'Greys',
    annotate: bool = False,
    title: Optional[str] = None,
) -> 'Figure':
    """Plot a heatmap of pitch distributions across segments.

    Mirrors the PitchPrevalence component from the IDTAP web app.

    Args:
        piece: The Piece to analyse.
        segmentation: How to segment — ``'section'``, ``'phrase'``, or
            ``'duration'``.
        output_type: ``'pitchNumber'`` or ``'chroma'``.
        pitch_representation: ``'pitch_onsets'`` (uses onset-based durations)
            or ``'fixed_pitch'`` (uses fixed-pitch durations).
        segment_duration: Duration in seconds when ``segmentation='duration'``.
        inst: Instrument index.
        ax: Existing Axes to draw on.
        figsize: Figure size if creating new Figure.
        cmap: Matplotlib colormap.
        annotate: Whether to annotate cells with percentage values.
        title: Optional title.

    Returns:
        The matplotlib Figure containing the heatmap.
    """
    import matplotlib.pyplot as plt

    # Build segment groups
    if segmentation == 'section':
        segments = _segments_from_sections(piece, inst)
        seg_labels = [f'S{i}' for i in range(len(segments))]
    elif segmentation == 'phrase':
        segments = [[t for p in [phrase] for t in p.trajectory_grid[0]]
                     for phrase in piece.phrase_grid[inst]]
        seg_labels = [f'P{i}' for i in range(len(segments))]
    elif segmentation == 'duration':
        segments = segment_by_duration(
            piece, duration=segment_duration, inst=inst,
        )
        seg_labels = [f'{i * segment_duration:.0f}s' for i in range(len(segments))]
    else:
        raise ValueError(f'Unknown segmentation: {segmentation}')

    if not segments:
        own_fig = ax is None
        if own_fig:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = ax.figure  # type: ignore[union-attr]
        ax.text(0.5, 0.5, 'No segments', transform=ax.transAxes,  # type: ignore[union-attr]
                ha='center', va='center')
        return fig

    # Compute pitch proportions per segment
    all_pitches: set = set()
    seg_pitch_durs: List[Dict] = []
    for seg_trajs in segments:
        if not seg_trajs:
            seg_pitch_durs.append({})
            continue
        if pitch_representation == 'pitch_onsets':
            durs = durations_of_pitch_onsets(
                seg_trajs, output_type=output_type,
                count_type='proportional',
            )
        else:
            # Use existing per-trajectory method
            durs: Dict = {}
            for t in seg_trajs:
                for k, v in t.durations_of_fixed_pitches(
                    {'output_type': output_type}
                ).items():
                    durs[k] = durs.get(k, 0) + v
            total = sum(durs.values())
            if total > 0:
                durs = {k: v / total for k, v in durs.items()}
        seg_pitch_durs.append(durs)
        all_pitches.update(durs.keys())

    if not all_pitches:
        own_fig = ax is None
        if own_fig:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = ax.figure  # type: ignore[union-attr]
        ax.text(0.5, 0.5, 'No pitch data', transform=ax.transAxes,  # type: ignore[union-attr]
                ha='center', va='center')
        return fig

    pitch_list = sorted(all_pitches)

    # Build 2D array: rows=pitches, cols=segments
    data = np.zeros((len(pitch_list), len(segments)))
    for col, durs in enumerate(seg_pitch_durs):
        for row, pitch in enumerate(pitch_list):
            data[row, col] = durs.get(pitch, 0.0)

    # Pitch labels
    if output_type == 'chroma':
        pitch_labels = [
            Pitch.from_pitch_number(int(p)).sargam_letter
            for p in pitch_list
        ]
    else:
        pitch_labels = [str(p) for p in pitch_list]

    # Plot
    own_fig = ax is None
    if own_fig:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure  # type: ignore[union-attr]

    im = ax.imshow(  # type: ignore[union-attr]
        data, aspect='auto', cmap=cmap, origin='lower',
        interpolation='nearest',
    )

    ax.set_xticks(range(len(seg_labels)))  # type: ignore[union-attr]
    ax.set_xticklabels(seg_labels, fontsize=8)  # type: ignore[union-attr]
    ax.set_yticks(range(len(pitch_labels)))  # type: ignore[union-attr]
    ax.set_yticklabels(pitch_labels, fontsize=8)  # type: ignore[union-attr]
    ax.set_xlabel('Segment')  # type: ignore[union-attr]
    ax.set_ylabel('Pitch')  # type: ignore[union-attr]

    if annotate:
        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                val = data[row, col]
                if val > 0:
                    ax.text(  # type: ignore[union-attr]
                        col, row, f'{val:.0%}',
                        ha='center', va='center', fontsize=6,
                        color='white' if val > 0.5 else 'black',
                    )

    fig.colorbar(im, ax=ax, label='Proportion')  # type: ignore[arg-type]

    if title:
        ax.set_title(title)  # type: ignore[union-attr]

    if own_fig:
        fig.tight_layout()

    return fig


def plot_pitch_patterns(
    piece_or_trajs,
    pattern_size: int = 3,
    max_patterns: int = 20,
    output_type: str = 'pitchNumber',
    inst: int = 0,
    ax: Optional['Axes'] = None,
    figsize: Tuple[float, float] = (10, 6),
    title: Optional[str] = None,
) -> 'Figure':
    """Visualise the most common pitch N-gram patterns.

    Mirrors the pattern analysis from the IDTAP web app's Analyzer component.

    Args:
        piece_or_trajs: Either a ``Piece`` (trajectories extracted from
            instrument *inst*) or an explicit list of Trajectories.
        pattern_size: N-gram size.
        max_patterns: Maximum number of patterns to display.
        output_type: Pitch representation for pattern detection.
        inst: Instrument index (used only when *piece_or_trajs* is a Piece).
        ax: Existing Axes.
        figsize: Figure size if creating new Figure.
        title: Optional title.

    Returns:
        The matplotlib Figure.
    """
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    if isinstance(piece_or_trajs, list):
        trajs = piece_or_trajs
    else:
        trajs = piece_or_trajs.all_trajectories(inst)

    patterns = pattern_counter(
        trajs, size=pattern_size, output_type=output_type,
    )
    patterns = patterns[:max_patterns]

    if not patterns:
        own_fig = ax is None
        if own_fig:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = ax.figure  # type: ignore[union-attr]
        ax.text(0.5, 0.5, 'No patterns found', transform=ax.transAxes,  # type: ignore[union-attr]
                ha='center', va='center')
        return fig

    own_fig = ax is None
    if own_fig:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure  # type: ignore[union-attr]

    n_patterns = len(patterns)
    cell_h = 0.8
    cell_w = 1.0

    for row_idx, pat in enumerate(reversed(patterns)):
        y = row_idx
        for col_idx, pitch_val in enumerate(pat['pattern']):
            if isinstance(pitch_val, (int, float)):
                color_idx = int(pitch_val) % 12
                color = CHROMA_COLORS[color_idx]
            else:
                color = '#cccccc'
            rect = Rectangle(
                (col_idx * cell_w, y + (1 - cell_h) / 2),
                cell_w * 0.9, cell_h,
                facecolor=color, edgecolor='white', linewidth=0.5,
            )
            ax.add_patch(rect)  # type: ignore[union-attr]
            ax.text(  # type: ignore[union-attr]
                col_idx * cell_w + cell_w * 0.45,
                y + 0.5,
                str(pitch_val),
                ha='center', va='center',
                fontsize=7, color='white', fontweight='bold',
            )

        # Count label
        ax.text(  # type: ignore[union-attr]
            pattern_size * cell_w + 0.3,
            y + 0.5,
            f'×{pat["count"]}',
            ha='left', va='center', fontsize=9,
        )

    ax.set_xlim(-0.1, pattern_size * cell_w + 1.5)  # type: ignore[union-attr]
    ax.set_ylim(-0.1, n_patterns + 0.1)  # type: ignore[union-attr]
    ax.set_yticks([])  # type: ignore[union-attr]
    ax.set_xticks([])  # type: ignore[union-attr]
    ax.set_aspect('equal')  # type: ignore[union-attr]
    ax.set_xlabel(f'{pattern_size}-gram patterns (most common)')  # type: ignore[union-attr]

    if title:
        ax.set_title(title)  # type: ignore[union-attr]

    if own_fig:
        fig.tight_layout()

    return fig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _segments_from_sections(piece: 'Piece', inst: int) -> List[List[Trajectory]]:
    """Split a piece's trajectories by section boundaries."""
    phrases = piece.phrase_grid[inst]
    section_starts = piece.section_starts_grid[inst]

    if not section_starts:
        # No sections — treat entire piece as one segment
        return [piece.all_trajectories(inst)]

    segments: List[List[Trajectory]] = []
    for sec_idx in range(len(section_starts)):
        start_phrase = section_starts[sec_idx]
        end_phrase = (
            section_starts[sec_idx + 1]
            if sec_idx + 1 < len(section_starts)
            else len(phrases)
        )
        trajs: List[Trajectory] = []
        for p_idx in range(start_phrase, end_phrase):
            if p_idx < len(phrases):
                trajs.extend(phrases[p_idx].trajectory_grid[0])
        segments.append(trajs)

    return segments
