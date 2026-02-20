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

# Sargam letter for each chroma value (0-11)
_CHROMA_SARGAM = {
    0: 'S', 1: 'r', 2: 'R', 3: 'g', 4: 'G',
    5: 'm', 6: 'M', 7: 'P', 8: 'd', 9: 'D',
    10: 'n', 11: 'N',
}


def _display_time(seconds: float) -> str:
    """Format seconds as m:ss or h:mm:ss, matching the web app."""
    total = int(round(seconds))
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    if h > 0:
        return f'{h}:{m:02d}:{s:02d}'
    return f'{m}:{s:02d}'


def _pitch_sargam_label(pitch_number: int) -> str:
    """Convert pitch number to sargam letter."""
    chroma = pitch_number % 12
    if chroma < 0:
        chroma += 12
    return _CHROMA_SARGAM.get(chroma, str(pitch_number))


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


# ---------------------------------------------------------------------------
# Pitch Prevalence — table-style grid matching the IDTAP web app
# ---------------------------------------------------------------------------

def plot_pitch_prevalence(
    piece: 'Piece',
    segmentation: str = 'section',
    output_type: str = 'pitchNumber',
    pitch_representation: str = 'fixed_pitch',
    condensed: bool = False,
    heatmap: bool = False,
    segment_duration: float = 10,
    inst: int = 0,
    fade_time: float = 5,
    figsize: Optional[Tuple[float, float]] = None,
    title: Optional[str] = None,
) -> 'Figure':
    """Plot a table-style pitch prevalence grid matching the IDTAP web app.

    Renders a grid of pitch duration percentages across time segments,
    faithfully mirroring the PitchPrevalence component from the web app.

    Three coloring modes:

    * **Standard** (``heatmap=False``, ``output_type='pitchNumber'``):
      Light-grey cells within pitch range; the mode pitch (highest %)
      is darker grey with white text.
    * **Pitch chroma** (``heatmap=False``, ``output_type='chroma'``):
      Individual light-grey cells per pitch; mode pitch in darker grey.
    * **Heatmap** (``heatmap=True``): White-to-black gradient per cell.

    Header rows show section/phrase metadata (number, start, duration, type).
    The Y-axis uses octave-grouped sargam letter labels.

    Args:
        piece: The Piece to analyse.
        segmentation: ``'section'``, ``'phrase'``, or ``'duration'``.
        output_type: ``'pitchNumber'`` or ``'chroma'``.
        pitch_representation: ``'fixed_pitch'`` or ``'pitch_onsets'``.
        condensed: Show only pitches that appear in data (fewer rows).
        heatmap: Use white-to-black gradient coloring.
        segment_duration: Seconds per segment when ``segmentation='duration'``.
        inst: Instrument index.
        fade_time: Max silence duration for pitch_onsets mode.
        figsize: Figure size (auto-calculated if *None*).
        title: Optional title shown above the grid.

    Returns:
        The matplotlib Figure.
    """
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    # ------------------------------------------------------------------ #
    # 1. Build segments + header metadata                                 #
    # ------------------------------------------------------------------ #
    segments: List[List[Trajectory]] = []
    seg_meta: List[Dict] = []

    if segmentation == 'section':
        sections = piece.sections_grid[inst]
        section_start_indices = piece.section_starts_grid[inst]
        phrase_starts = piece.dur_starts(inst)

        for sec_i, section in enumerate(sections):
            trajs: List[Trajectory] = []
            for phrase in section.phrases:
                trajs.extend(phrase.trajectory_grid[0])
            segments.append(trajs)

            # Start time
            if sec_i < len(section_start_indices):
                pi = section_start_indices[sec_i]
                start = phrase_starts[pi] if pi < len(phrase_starts) else 0.0
            else:
                start = 0.0

            # End time
            if sec_i + 1 < len(section_start_indices):
                npi = section_start_indices[sec_i + 1]
                end = phrase_starts[npi] if npi < len(phrase_starts) else (piece.dur_tot or 0)
            else:
                end = piece.dur_tot or 0

            # Section type from categorization
            sec_type = 'None'
            cat = section.categorization
            if cat:
                tl = cat.get('Top Level')
                if isinstance(tl, str) and tl != 'None':
                    sec_type = tl
                else:
                    for cat_name, cat_val in cat.items():
                        if cat_name == 'Top Level':
                            continue
                        if isinstance(cat_val, dict):
                            for k, v in cat_val.items():
                                if v:
                                    sec_type = k
                                    break
                        if sec_type != 'None':
                            break

            seg_meta.append({
                'number': sec_i + 1,
                'start': start,
                'duration': end - start,
                'type': sec_type,
            })

    elif segmentation == 'phrase':
        phrases = piece.phrase_grid[inst]
        phrase_starts = piece.dur_starts(inst)
        section_start_indices = piece.section_starts_grid[inst]

        # Build section index for each phrase
        sections_list = piece.sections_grid[inst]
        sec_cats = piece.section_cat_grid[inst] if hasattr(piece, 'section_cat_grid') else []

        for p_i, phrase in enumerate(phrases):
            segments.append(list(phrase.trajectory_grid[0]))
            start = phrase_starts[p_i] if p_i < len(phrase_starts) else 0.0

            # Which section does this phrase belong to?
            sec_idx = 0
            for si, ss in enumerate(section_start_indices):
                if p_i >= ss:
                    sec_idx = si

            # Section type
            sec_type = ''
            if sec_idx < len(sec_cats):
                cat = sec_cats[sec_idx]
                tl = cat.get('Top Level', '')
                if isinstance(tl, str) and tl != 'None':
                    sec_type = tl

            # Extract phrase categorization
            pcat = phrase.categorization_grid[0] if phrase.categorization_grid else {}
            phrase_types = [k for k, v in pcat.get('Phrase', {}).items() if v]
            elaborations = [k for k, v in pcat.get('Elaboration', {}).items() if v]
            vocal_arts = [k for k, v in pcat.get('Vocal Articulation', {}).items() if v]
            inst_arts = [k for k, v in pcat.get('Instrumental Articulation', {}).items() if v]
            articulations = vocal_arts or inst_arts
            incidentals = [k for k, v in pcat.get('Incidental', {}).items() if v]

            seg_meta.append({
                'number': p_i + 1,
                'start': start,
                'duration': phrase.dur_tot or 0,
                'is_section_start': p_i in section_start_indices,
                'section_number': sec_idx + 1,
                'section_type': sec_type,
                'phrase_type': ', '.join(phrase_types),
                'elaboration': ', '.join(elaborations),
                'articulation': ', '.join(articulations),
                'incidental': ', '.join(incidentals),
            })

    elif segmentation == 'duration':
        segments = segment_by_duration(
            piece, duration=segment_duration, inst=inst,
        )
        for i in range(len(segments)):
            seg_meta.append({'start': i * segment_duration})
    else:
        raise ValueError(f'Unknown segmentation: {segmentation}')

    n_seg = len(segments)
    if n_seg == 0:
        fig, ax = plt.subplots(figsize=figsize or (10, 6))
        ax.text(0.5, 0.5, 'No segments', transform=ax.transAxes,
                ha='center', va='center')
        return fig

    # ------------------------------------------------------------------ #
    # 2. Compute pitch durations per segment                              #
    # ------------------------------------------------------------------ #
    from .classes.piece import durations_of_fixed_pitches as _dofp

    seg_durs: List[Dict] = []
    for seg_trajs in segments:
        if not seg_trajs:
            seg_durs.append({})
            continue
        if pitch_representation == 'pitch_onsets':
            durs = durations_of_pitch_onsets(
                seg_trajs, output_type=output_type,
                count_type='proportional', max_silence=fade_time,
            )
        else:
            durs = _dofp(seg_trajs, output_type=output_type,
                         count_type='proportional')
        seg_durs.append(durs)

    # ------------------------------------------------------------------ #
    # 3. Determine pitch rows                                             #
    # ------------------------------------------------------------------ #
    all_pitches: set = set()
    for d in seg_durs:
        all_pitches.update(k for k, v in d.items() if isinstance(k, (int, float)) and v > 0)

    if not all_pitches:
        fig, ax = plt.subplots(figsize=figsize or (10, 6))
        ax.text(0.5, 0.5, 'No pitch data', transform=ax.transAxes,
                ha='center', va='center')
        return fig

    lo = int(min(all_pitches))
    hi = int(max(all_pitches))

    if output_type == 'chroma':
        pitch_rows = sorted(set(int(p) for p in all_pitches))
    elif condensed:
        pitch_rows = sorted(int(p) for p in all_pitches)
    else:
        pitch_rows = list(range(lo, hi + 1))

    # Display order: high pitches at top → reversed for drawing bottom-up
    pitch_rows_display = list(reversed(pitch_rows))  # index 0 = highest pitch
    n_rows = len(pitch_rows_display)

    # ------------------------------------------------------------------ #
    # 4. Sargam labels + octave grouping                                  #
    # ------------------------------------------------------------------ #
    sargam_labels = [_pitch_sargam_label(p) for p in pitch_rows_display]

    # Octave groups (for pitchNumber mode, non-chroma)
    # Always group by semitone octave (// 12) regardless of condensed mode,
    # since pitch numbers are always in semitones.
    octave_groups: Dict[int, List[int]] = {}  # oct -> list of display-row indices
    if output_type != 'chroma':
        for ri, p in enumerate(pitch_rows_display):
            oct_num = p // 12
            octave_groups.setdefault(oct_num, []).append(ri)

    # ------------------------------------------------------------------ #
    # 5. Header layout                                                    #
    # ------------------------------------------------------------------ #
    if segmentation == 'section':
        header_row_labels = ['Section #', 'Start', 'Duration', 'Sec. Type']
    elif segmentation == 'phrase':
        # Bottom (closest to pitch grid) → top; spanning rows at top
        header_row_labels = [
            'Incidental', 'Articulation', 'Elaboration', 'Phrase Type',
            'Duration', 'Start', 'Phrase #',
            'Section', 'Section #',
        ]
    else:
        header_row_labels = ['Start']
    n_header = len(header_row_labels)

    # Section spans for phrase-mode merged header cells
    section_spans: List[Tuple[int, int, int, str]] = []
    if segmentation == 'phrase':
        _cur_sec = None
        _span_start = 0
        for _ci, _meta in enumerate(seg_meta):
            _sec_num = _meta.get('section_number')
            if _sec_num != _cur_sec:
                if _cur_sec is not None:
                    section_spans.append((
                        _span_start, _ci, _cur_sec,
                        seg_meta[_span_start].get('section_type', ''),
                    ))
                _cur_sec = _sec_num
                _span_start = _ci
        if _cur_sec is not None:
            section_spans.append((
                _span_start, n_seg, _cur_sec,
                seg_meta[_span_start].get('section_type', ''),
            ))

    # ------------------------------------------------------------------ #
    # 6. Figure setup — adaptive sizing per segmentation mode             #
    #    Web-app style: wider columns, shorter rows                       #
    # ------------------------------------------------------------------ #
    if segmentation == 'phrase':
        cell_w = max(0.45, min(0.85, 50.0 / max(n_seg, 1)))
        cell_h = 0.22
        left_margin = 3.2
        font_cell = 5.0
        font_header = 5.0
        font_label = 6.5
    elif segmentation == 'duration':
        cell_w = max(0.7, min(1.5, 40.0 / max(n_seg, 1)))
        cell_h = 0.38
        left_margin = 2.8
        font_cell = 7.0
        font_header = 7.0
        font_label = 8.0
    else:  # section
        cell_w = max(1.0, min(1.8, 22.0 / max(n_seg, 1)))
        cell_h = 0.42
        left_margin = 2.8
        font_cell = 7.0
        font_header = 7.0
        font_label = 8.0

    header_height = n_header * cell_h

    if figsize is None:
        fw = max(10, min(50, left_margin + n_seg * cell_w + 1))
        fh = max(5, min(30, (n_rows + n_header) * cell_h + 3))
        figsize = (fw, fh)

    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(-left_margin - 0.2, n_seg * cell_w + 0.2)
    ax.set_ylim(-0.5, n_rows * cell_h + header_height + 1.5)
    ax.set_aspect('auto')
    ax.axis('off')

    # ------------------------------------------------------------------ #
    # 7. Draw header rows                                                 #
    # ------------------------------------------------------------------ #
    header_y0 = n_rows * cell_h  # bottom edge of header area
    _spanning_labels = {'Section #', 'Section'}

    for hi, label in enumerate(header_row_labels):
        hy = header_y0 + hi * cell_h

        # Row label on the left
        ax.text(-left_margin / 2, hy + cell_h / 2, label,
                ha='center', va='center', fontsize=font_header,
                fontweight='bold')

        if segmentation == 'phrase' and label in _spanning_labels:
            # Draw merged cells spanning across phrases in same section
            for sp_start, sp_end, sec_num, sec_type in section_spans:
                sx = sp_start * cell_w
                sw = (sp_end - sp_start) * cell_w
                val = str(sec_num) if label == 'Section #' else sec_type

                rect = Rectangle(
                    (sx, hy), sw, cell_h,
                    facecolor='#F0F0F0', edgecolor='black', linewidth=0.5,
                )
                ax.add_patch(rect)
                ax.text(sx + sw / 2, hy + cell_h / 2, val,
                        ha='center', va='center', fontsize=font_header,
                        clip_on=True)
        else:
            # Per-segment values
            for ci in range(n_seg):
                meta = seg_meta[ci]
                cx = ci * cell_w + cell_w / 2

                if label in ('Section #', 'Phrase #'):
                    val = str(meta.get('number', ci + 1))
                elif label == 'Start':
                    val = _display_time(meta.get('start', 0))
                elif label == 'Duration':
                    val = _display_time(meta.get('duration', 0))
                elif label == 'Sec. Type':
                    val = str(meta.get('type', 'None'))
                elif label == 'Phrase Type':
                    val = meta.get('phrase_type', '')
                elif label == 'Elaboration':
                    val = meta.get('elaboration', '')
                elif label == 'Articulation':
                    val = meta.get('articulation', '')
                elif label == 'Incidental':
                    val = meta.get('incidental', '')
                else:
                    val = ''

                ax.text(cx, hy + cell_h / 2, val,
                        ha='center', va='center', fontsize=font_header,
                        clip_on=True)

    # Header grid lines — horizontal lines across full width,
    # but skip lines that cut through spanning rows internally.
    # Find where the spanning area starts (only in phrase mode).
    _span_start_hi = n_header  # default: no spanning (vlines go full height)
    if segmentation == 'phrase':
        for _hi, _lbl in enumerate(header_row_labels):
            if _lbl in _spanning_labels:
                _span_start_hi = _hi
                break

    for hi in range(n_header + 1):
        hy = header_y0 + hi * cell_h
        ax.plot([-left_margin, n_seg * cell_w], [hy, hy],
                color='black', linewidth=0.5, clip_on=False)

    # Vertical lines in header — only through the non-spanning rows.
    # The spanning rows have their own Rectangle borders at section edges.
    _vtop = header_y0 + _span_start_hi * cell_h  # stop vlines here
    for ci in range(n_seg + 1):
        cx = ci * cell_w
        ax.plot([cx, cx], [header_y0, _vtop],
                color='#D3D3D3', linewidth=0.5, clip_on=False)

    # ------------------------------------------------------------------ #
    # 8. Draw pitch grid cells                                            #
    # ------------------------------------------------------------------ #
    for ci, durs in enumerate(seg_durs):
        # Mode pitch for this segment (highest proportion)
        mode_pitch = None
        mode_val = 0.0
        for pk, pv in durs.items():
            if isinstance(pk, (int, float)) and pv > mode_val:
                mode_val = pv
                mode_pitch = pk

        # Pitches present in this segment (for range-box in standard mode)
        seg_present = {int(k) for k, v in durs.items()
                       if isinstance(k, (int, float)) and v > 0}
        seg_lo = min(seg_present) if seg_present else None
        seg_hi = max(seg_present) if seg_present else None

        for ri, pitch in enumerate(pitch_rows_display):
            val = durs.get(pitch, 0.0)
            # Also try int key if pitch is int
            if val == 0.0 and isinstance(pitch, int):
                val = durs.get(float(pitch), 0.0)

            x = ci * cell_w
            y = (n_rows - 1 - ri) * cell_h  # bottom-up

            # ---- Determine cell color ----
            if heatmap:
                if val > 0:
                    g = 1.0 - val
                    color = (g, g, g)
                    text_color = 'white' if val > 0.5 else 'black'
                else:
                    color = 'white'
                    text_color = 'black'
            elif output_type == 'chroma':
                # Pitch-chroma mode: individual cells
                if val > 0:
                    color = 'grey' if pitch == mode_pitch else '#D3D3D3'
                    text_color = 'white' if pitch == mode_pitch else 'black'
                else:
                    color = 'white'
                    text_color = 'black'
            else:
                # Standard mode: light grey for range, darker for mode
                in_range = (seg_lo is not None and seg_lo <= pitch <= seg_hi)
                if val > 0 and pitch == mode_pitch:
                    color = 'grey'
                    text_color = 'white'
                elif in_range:
                    color = '#D3D3D3'
                    text_color = 'black'
                else:
                    color = 'white'
                    text_color = 'black'

            rect = Rectangle(
                (x, y), cell_w, cell_h,
                facecolor=color,
                edgecolor='#E0E0E0',
                linewidth=0.3,
            )
            ax.add_patch(rect)

            # Percentage text
            if val > 0:
                pct_str = f'{val * 100:.0f}%'
                ax.text(x + cell_w / 2, y + cell_h / 2, pct_str,
                        ha='center', va='center',
                        fontsize=font_cell, color=text_color)

    # ------------------------------------------------------------------ #
    # 9. Y-axis labels: sargam letters                                    #
    # ------------------------------------------------------------------ #
    for ri, (pitch, slabel) in enumerate(zip(pitch_rows_display, sargam_labels)):
        y = (n_rows - 1 - ri) * cell_h + cell_h / 2
        ax.text(-0.3, y, slabel,
                ha='right', va='center', fontsize=font_label)

    # ------------------------------------------------------------------ #
    # 10. Octave grouping boxes                                           #
    # ------------------------------------------------------------------ #
    if octave_groups:
        oct_box_x = -left_margin
        oct_box_w = left_margin - 1.2  # leave room for sargam labels

        for oct_num, row_indices in sorted(octave_groups.items(), reverse=True):
            top_ri = min(row_indices)
            bot_ri = max(row_indices)
            top_y = (n_rows - 1 - top_ri) * cell_h + cell_h
            bot_y = (n_rows - 1 - bot_ri) * cell_h

            # Octave label
            mid_y = (top_y + bot_y) / 2
            ax.text(oct_box_x + oct_box_w / 2, mid_y, str(oct_num),
                    ha='center', va='center', fontsize=9, fontweight='bold')

            # Octave box outline
            rect = Rectangle(
                (oct_box_x, bot_y), oct_box_w, top_y - bot_y,
                facecolor='none', edgecolor='black', linewidth=0.8,
            )
            ax.add_patch(rect)

            # Horizontal separator at bottom of this octave
            ax.plot([oct_box_x + oct_box_w, n_seg * cell_w],
                    [bot_y, bot_y],
                    color='black', linewidth=0.5, clip_on=False)

    # ------------------------------------------------------------------ #
    # 11. Grid border lines                                               #
    # ------------------------------------------------------------------ #
    # Vertical column separators in pitch grid (light grey, internal)
    for ci in range(1, n_seg):
        cx = ci * cell_w
        ax.plot([cx, cx], [0, n_rows * cell_h],
                color='#D3D3D3', linewidth=0.4, clip_on=False)

    # Mark section boundaries with black vertical lines (phrase mode)
    if segmentation == 'phrase':
        for ci, meta in enumerate(seg_meta):
            if meta.get('is_section_start') and ci > 0:
                cx = ci * cell_w
                ax.plot([cx, cx], [0, n_rows * cell_h + header_height],
                        color='black', linewidth=1.2, clip_on=False)

    # Full outer border around data grid
    _grid_h = n_rows * cell_h + header_height
    _border = Rectangle(
        (0, 0), n_seg * cell_w, _grid_h,
        facecolor='none', edgecolor='black', linewidth=2.0, zorder=10,
    )
    ax.add_patch(_border)

    # Horizontal line separating pitch grid from header
    ax.plot([0, n_seg * cell_w], [n_rows * cell_h, n_rows * cell_h],
            color='black', linewidth=0.8, clip_on=False, zorder=10)

    # Outer left border — encloses Y-axis labels and octave boxes
    _outer_border = Rectangle(
        (-left_margin, 0), left_margin + n_seg * cell_w, _grid_h,
        facecolor='none', edgecolor='black', linewidth=2.0, zorder=10,
    )
    ax.add_patch(_outer_border)

    # ------------------------------------------------------------------ #
    # 12. Titles and subtitles                                            #
    # ------------------------------------------------------------------ #
    top_y = n_rows * cell_h + header_height

    # Piece title
    piece_title = title or getattr(piece, 'title', '')
    if piece_title:
        ax.text(n_seg * cell_w / 2, top_y + 1.0, piece_title,
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    # Subtitle
    pr_label = 'Fixed Pitch' if pitch_representation == 'fixed_pitch' else 'Pitch Onsets'
    if segmentation == 'section':
        subtitle = f'Pitch Range and Percentage of Duration on each {pr_label}, Segmented by Section'
    elif segmentation == 'phrase':
        subtitle = f'Pitch Range and Percentage of Duration on each {pr_label}, Segmented by Phrase'
    else:
        subtitle = (f'Pitch Range and Percentage of Duration on each {pr_label}, '
                     f'Segmented into {segment_duration:.0f}s Windows')
    ax.text(n_seg * cell_w / 2, top_y + 0.4, subtitle,
            ha='center', va='bottom', fontsize=7, style='italic')

    fig.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.02)
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
