Spectrogram Analysis
====================

Spectrogram data access and visualization for audio analysis.

.. currentmodule:: idtap

SpectrogramData
---------------

The :class:`SpectrogramData` class provides comprehensive access to Constant-Q Transform (CQT)
spectrograms for computational musicology and audio analysis.

.. autoclass:: SpectrogramData
   :members:
   :undoc-members:
   :show-inheritance:

Key Features
~~~~~~~~~~~~

* **Constant-Q Transform (CQT)** - Log-spaced frequency bins for musical analysis
* **Intensity Transformation** - Power-law contrast enhancement (1.0-5.0)
* **Colormap Support** - 35+ matplotlib colormaps
* **Frequency/Time Cropping** - Extract specific frequency ranges or time segments
* **Matplotlib Integration** - Plot on existing axes for overlays with pitch contours
* **Image Export** - Save as PNG, JPEG, WebP, etc.

Quick Examples
~~~~~~~~~~~~~~

Load and display a spectrogram::

    from idtap import SwaraClient, SpectrogramData

    client = SwaraClient()
    spec = SpectrogramData.from_audio_id("audio_id_here", client)

    # Save basic visualization
    spec.save("output.png", power=2.0, cmap='viridis')

Create matplotlib overlay with pitch contour::

    import matplotlib.pyplot as plt

    # Load spectrogram and piece data
    spec = SpectrogramData.from_piece(piece, client)

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot spectrogram as underlay with transparency
    im = spec.plot_on_axis(ax, power=2.0, cmap='viridis', alpha=0.7, zorder=0)

    # Overlay pitch contour
    times = [traj.start_time for traj in piece.trajectories]
    pitches = [traj.pitch_contour[0] for traj in piece.trajectories]
    ax.plot(times, pitches, 'r-', linewidth=2, zorder=1)

    # Configure axes
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Frequency (Hz)')
    plt.colorbar(im, ax=ax, label='Intensity')

    plt.savefig('overlay.png', dpi=150, bbox_inches='tight')

Crop to specific region::

    # Extract 200-800 Hz range, first 10 seconds
    cropped = spec.crop_frequency(200, 800).crop_time(0, 10)
    cropped.save("cropped.png", power=2.5, cmap='magma')

Supported Colormaps
~~~~~~~~~~~~~~~~~~~

.. autodata:: SUPPORTED_COLORMAPS
   :annotation:

Available colormaps include: viridis, plasma, magma, inferno, hot, cool, gray, and many more.
See the matplotlib colormap documentation for visual examples.

Technical Details
~~~~~~~~~~~~~~~~~

* **Algorithm**: Essentia NSGConstantQ (Non-Stationary Gabor Constant-Q Transform)
* **Default Frequency Range**: 75-2400 Hz
* **Default Bins Per Octave**: 72 (high resolution for microtonal analysis)
* **Data Format**: uint8 grayscale (0-255), gzip-compressed
* **Time Resolution**: ~0.0116 seconds per frame (typical)
* **Frequency Scale**: Logarithmic (perceptually-uniform for music)
