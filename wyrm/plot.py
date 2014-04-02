#!/usr/bin/env python
"""Plotting methods.

This module contains various plotting methods.

"""

from __future__ import division

import numpy as np
from scipy import interpolate

from matplotlib import axes
from matplotlib import colorbar
from matplotlib import colors
from matplotlib import pyplot as plt
from matplotlib.path import Path
from matplotlib import patches as patches
from matplotlib.patches import Rectangle

import tentensystem as tts


def plot_channels(dat, chanaxis=-1, otheraxis=-2):
    """Plot all channels for a continuous.

    Parameters
    ----------
    dat : Data

    """
    ax = []
    n_channels = dat.data.shape[chanaxis]
    for i, chan in enumerate(dat.axes[chanaxis]):
        if i == 0:
            a = plt.subplot(10, n_channels / 10 + 1, i + 1)
        else:
            a = plt.subplot(10, n_channels / 10 + 1, i + 1, sharex=ax[0], sharey=ax[0])
        ax.append(a)
        #x, y = dat.axes[otheraxis], dat.data.take([i], chanaxis)
        dat.axes[otheraxis], dat.data.take([i], chanaxis)
        a.plot(dat.axes[otheraxis], dat.data.take([i], chanaxis).squeeze())
        a.set_title(chan)
        plt.axvline(x=0)
        plt.axhline(y=0)


def plot_spectrum(spectrum, freqs):
    plt.plot(freqs, spectrum, '.')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('[dl]')


def plot_spectrogram(spectrogram, freqs):
    extent = 0, len(spectrogram), freqs[0], freqs[-1]
    plt.imshow(spectrogram.transpose(),
               aspect='auto',
               origin='lower',
               extent=extent,
               interpolation='none')
    plt.colorbar()
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time')


def calculate_stereographic_projection(p):
    """Calculate the stereographic projection.

    Given a unit sphere with radius ``r = 1`` and center at the origin.
    Project the point ``p = (x, y, z)`` from the sphere's South pole (0,
    0, -1) on a plane on the sphere's North pole (0, 0, 1).

    The formula is:

        P' = P * (2r / (r + z))

    Parameters
    ----------
    p : [float, float]
        The point to be projected in cartesian coordinates.

    Returns
    -------
    x, y : float, float
        The projected point on the plane.

    """
    # P' = P * (2r / r + z)
    # changed the values to move the point of projection further below the
    # south pole
    mu = 1 / (1.3 + p[2])
    x = p[0] * mu
    y = p[1] * mu
    return x, y


def interpolate_2d(x, y, z):
    """Interpolate missing points on a plane.

    Parameters
    ----------
    x, y, z : equally long lists of floats
        1d arrays defining points like ``p[x, y] = z``

    Returns
    -------
    X, Y, Z : 1d array, 1d array, 2d array
        ``Z`` is a 2d array ``[min(x)..max(x), [min(y)..max(y)]`` with
        the interpolated values as values.

    """
    xx = np.linspace(min(x), max(x))
    yy = np.linspace(min(y), max(y))
    xx, yy = np.meshgrid(xx, yy)
    f = interpolate.LinearNDInterpolator(zip(x, y), z)
    zz = f(xx, yy)
    return xx, yy, zz


def bwr_cmap():
    """Create a linear segmented colormap with transitions from blue over white
    to red.

    Returns
    -------
    x : colormap
        The matplotlib colormap.
    """
    cdict = {'red': [(0.0, 0.0, 0.0),
                     (0.25, 0.0, 0.0),
                     (0.5, 1.0, 1.0),
                     (0.75, 1.0, 1.0),
                     (1.0, 0.5, 0.5)],

             'green': [(0.0, 0.0, 0.0),
                       (0.15, 0.0, 0.0),
                       (0.25, 1.0, 1.0),
                       (0.5, 1.0, 1.0),
                       (0.75, 1.0, 1.0),
                       (0.85, 0.0, 0.0),
                       (1.0, 0.0, 0.0)],

             'blue': [(0.0, 0.5, 0.5),
                      (0.25, 1.0, 1.0),
                      (0.5, 1.0, 1.0),
                      (0.75, 0.0, 0.0),
                      (1.0, 0.0, 0.0)]}

    return colors.LinearSegmentedColormap('bwr_colormap', cdict, 256)


def wr_cmap():
    """Create a linear segmented colormap with transitions from white to red.

    Returns
    -------
    x : colormap
        The matplotlib colormap.
    """
    cdict = {'red': [(0.0, 1.0, 1.0),
                     (0.75, 1.0, 1.0),
                     (1.0, .3, .3)],

             'green': [(0.0, 1.0, 1.0),
                       (0.75, 0.0, 0.0),
                       (1.0, 0.0, 0.0)],

             'blue': [(0.0, 1.0, 1.0),
                      (0.75, 0.0, 0.0),
                      (1.0, 0.0, 0.0)]}

    return colors.LinearSegmentedColormap('bwr_colormap', cdict, 256)


def plot_timeinterval(data, r_square=None, highlights=None, hcolors=None,
                      legend=True, channel=None, position=None):
    """Plots a simple time interval.

    <Longer Description>

    Parameters
    ----------
    data : wyrm.types.Data
        Data object containing the data to plot.
    r_square : [values], optional
        List containing r_squared values to be plotted beneath the main plot (default: None).
    highlights : [[int, int)]
        List of tuples containing the start point (included) and end point
        (excluded) of each area to be highlighted (default: None).
    hcolors : [colors], optional
        A list of colors to use for the highlights areas (default: None).
    legend : Boolean, optional
        Flag to switch plotting of the legend on or off (default: True).
    channel : int, optional
        A number to specify a single channel, which will then be plotted exclusively (default: None).
    position : [x, y, width, height], optional
        A Rectangle that limits the plot to its boundaries (default: None).

    Returns
    -------
    Matplotlib.Axes or (Matplotlib.Axes, Matplotlib.Axes)
        The Matplotlib.Axes corresponding to the plotted timeinterval. If r-square values where
        plotted, too, a second Matplotlib.Axes is returned alongside.

    Examples
    --------
    Plots all channels contained in data with a legend.

    >>> plot_timeinterval(data)

    Same as above, but without the legend.

    >>> plot_timeinterval(data, legend=False)

    Adds r-square values to the plot.

    >>> plot_timeinterval(data, r_square=[values], legend=False)

    Saves the plot automatically to 'path' as a pdf.

    >>> plot_timeinterval(data, r_square=[values], legend=False, save=True, save_path=path, save_format='pdf')
    """

    rect_ti_solo = [.07, .07, .9, .9]
    rect_ti_r2 = [.07, .12, .9, .85]
    rect_r2 = [.07, .07, .9, .05]

    if position is None:
        plt.figure()
        if r_square is None:
            pos_ti = rect_ti_solo
        else:
            pos_ti = rect_ti_r2
            pos_r2 = rect_r2
    else:
        if r_square is None:
            pos_ti = _transform_rect(position, rect_ti_solo)
        else:
            pos_ti = _transform_rect(position, rect_ti_r2)
            pos_r2 = _transform_rect(position, rect_r2)

    ax1 = None
    # plotting of the data
    ax0 = _subplot_timeinterval(data, position=pos_ti, epoch=-1, highlights=highlights,
                                hcolors=hcolors, legend=legend, channel=channel)
    ax0.xaxis.labelpad = 0
    if r_square is not None:
        ax1 = _subplot_r_square(r_square, position=pos_r2)
        ax0.tick_params(axis='x', direction='in', pad=30 * pos_ti[3])

    plt.grid(True)

    if r_square is None:
        return ax0
    else:
        return ax0, ax1


#todo: refactor plot_timeinterval so that this functionality is built in
def plot_epoched_timeinterval(data, highlights=None, hcolors=None, legend=True):
    """Plots a series of time_intervals with the given epoched data.

    <Longer Description>

    Parameters
    ----------
    data : wyrm.types.Data
        data object containing the data to plot.
    highlights : [[int, int)]
        List of tuples containing the start point (included) and end point
        (excluded) of each area to be highlighted.
    hcolors : [colors], optional
        A list of colors to use for the highlights areas.
    legend : Boolean, optional
        Flag to switch plotting of the legend on or off (default: True).

    Returns:
    --------
    [Matplotlib.Axes]
        Returns a list of Matplotlib.Axes, one for every epoch.
    """
    plt.figure()
    ax = []

    # check of data is epoched
    if len(data.data.shape) > 2:
        # iterate over epochs
        for i in range(len(data.data)):
            grid = calc_grid(len(data.data), 1, .04, .04)

            ax.append(_subplot_timeinterval(data, grid[i], i, highlights=highlights,
                                            hcolors=hcolors, legend=legend))
    else:
        pos = 111
        ax.append(_subplot_timeinterval(data, pos, -1, highlights=highlights, legend=legend))

    # add labels
    set_labels(data.units[len(data.axes) - 2], "$\mu$V", draw=False)

    # adjust the spacing
    plt.subplots_adjust(left=0.03, right=0.97, top=0.97, bottom=0.1, hspace=0.3, wspace=0.3)

    return ax


def plot_tenten(data, highlights=None, hcolors=None, legend=False):
    """Plots channels on a grid system.

    Plots all recognized channels on a grid system according to their positions
    on the scalp.

    Parameters
    ----------
    data : wyrm.types.Data
        Data object containing the data to plot.
    highlights : [[int, int)]
        List of tuples containing the start point (included) and end point
        (excluded) of each area to be highlighted (default: None).
    hcolors : [colors], optional
        A list of colors to use for the highlights areas (default: None).
    legend : Boolean, optional
        Flag to switch plotting of the legend on or off (default: True).

    Returns
    -------
    [Matplotlib.Axes], Matplotlib.Axes
        Returns the plotted timeinterval axes as a list of Matplotlib.Axes and the plotted scale as
        a single Matplotlib.Axes.
    """
    # this dictionary determines which y-position corresponds with which row in the grid
    ordering = {4.0: 0,
                3.5: 0,
                3.0: 1,
                2.5: 2,
                2.0: 3,
                1.5: 4,
                1.0: 5,
                0.5: 6,
                0.0: 7,
                -0.5: 8,
                -1.0: 9,
                -1.5: 10,
                -2.0: 11,
                -2.5: 12,
                -2.6: 12,
                -3.0: 13,
                -3.5: 14,
                -4.0: 15,
                -4.5: 15,
                -5.0: 16}

    # all the channels with their x- and y-position
    system = _get_system()

    # create list with 17 empty lists. one for every potential row of channels.
    channel_lists = []
    for i in range(18):
        channel_lists.append([])

    # distribute the channels to the lists by their y-position
    count = 0
    for c in data.axes[1]:
        if c in tts.channels:
            # entries in channel_lists: [<channel_name>, <x-position>, <position in Data>]
            channel_lists[ordering[system[c][1]]].append((c, system[c][0], count))
        count += 1

    # sort the lists of channels by their x-position
    for l in channel_lists:
        l.sort(key=lambda c_list: c_list[1])

    # calculate the needed dimensions of the grid
    columns = map(len, channel_lists)
    columns = [value for value in columns if value != 0]

    # add another axes to the first row for the scale
    columns[0] += 1

    plt.figure()
    grid = calc_centered_grid(columns, hpad=.01, vpad=.01)

    # axis used for sharing axes between channels
    masterax = None
    ax = []

    row = 0
    k = 0
    scale_ax = 0

    for l in channel_lists:
        if len(l) > 0:
            for i in range(len(l)):
                ax.append(_subplot_timeinterval(data, grid[k], epoch=-1, highlights=highlights, hcolors=hcolors, labels=False,
                                                legend=legend, channel=l[i][2], shareaxis=masterax))
                if masterax is None and len(ax) > 0:
                    masterax = ax[0]

                # hide the axeslabeling
                plt.tick_params(axis='both', which='both', labelbottom='off', labeltop='off', labelleft='off',
                                labelright='off', top='off', right='off')

                # at this moment just to show what's what
                plt.gca().annotate(l[i][0], (0.05, 0.05), xycoords='axes fraction')

                k += 1

                if row == 0 and i == len(l)-1:
                    # this is the last axes in the first row
                    scale_ax = k
                    k += 1

            row += 1

    # plot the scale axes
    xtext = data.axes[0][len(data.axes[0])-1]
    sc = _subplot_scale(str(xtext) + ' ms', "$\mu$V", position=grid[scale_ax])

    return ax, sc


def plot_scalp(v, channels, levels=25, colormap=None, norm=None, ticks=None,
               annotate=True, position=None):
    """Plots the values v for channels 'channels' on a scalp as a contour plot.

    Parameters
    ----------
    v : [values]
        List containing the values of the channels.
    channels : [String]
        List containing the channel names.
    levels : int, optional
        The number of automatically created levels in the contour plot (default: 25).
    colormap : matplotlib.colors.colormap, optional
        A colormap to define the color transitions (default: a blue-white-red colormap).
    norm : matplotlib.colors.norm, optional
        A norm to define the min and max values. (default: 'None', values from -10 to 10 are assumed).
    ticks : array([ints]), optional
        An array with values to define the ticks on the colorbar. If 'None' 3 ticks at -10, 0 and 10
        are displayed (default: None).
    annotate : Boolean, optional
        Flag to switch channel annotations on or off (default: True).
    position : [x, y, width, height], optional
        A Rectangle that limits the plot to its boundaries (default: None).

    Returns
    -------
    (Matplotlib.Axes, Matplotlib.Axes)
        Returns a pair of Matplotlib.Axes. The first contains the plotted scalp, the second the corresponding colorbar.
    """
    rect_scalp = [.05, .05, .8, .9]
    rect_colorbar = [.9, .05, .05, .9]

    plt.figure(figsize=[8, 6.5])

    if position is None:
        pos_scalp = rect_scalp
        pos_colorbar = rect_colorbar
    else:
        pos_scalp = _transform_rect(position, rect_scalp)
        pos_colorbar = _transform_rect(position, rect_colorbar)

    if colormap is None:
        colormap = bwr_cmap()
    if norm is None:
        norm = colors.Normalize(vmin=-10, vmax=10, clip=False)
    if ticks is None:
        ticks = np.linspace(-10.0, 10.0, 3, endpoint=True)

    ax0 = _subplot_scalp(v, channels, position=pos_scalp, levels=levels, colormap=colormap, annotate=annotate,
                         norm=norm)
    ax1 = _subplot_colorbar(position=pos_colorbar, colormap=colormap, ticks=ticks, norm=norm)

    return ax0, ax1


# todo: scale the labelsize (ax.get_xticklabels()[0].get_size(), x_labelsize *= rect[2]**0.5, ...
# ax.xaxis.set_tick_params(labelsize=x_labelsize)
# todo: refactor with new input parameters
def plot_scalp_ti(v, chans, data, interval, scale_ti=.1, levels=25, colormap=None,
                  norm=None, ticks=None, annotate=True, position=None):
    """Plots a scalp with channels on top

    Plots the values v for channels 'channels' on a scalp as a contour plot.
    Additionaly plots the channels in channels_ti as a timeinterval on top of
    the scalp plot. The individual channels are placed over their position on
    the scalp.

    Parameters
    ----------
    data : wyrm.types.Data
        Data object containing the data to plot.
    time : int
        The point in time to create the scalp plot from.
    channels_ti : [String]
        List containing the channel names for the overlaying timeinterval plots.
    scale_ti : float, optional
        The percentage to scale the overlaying timeinterval plots (default: 0.1).
    levels : int, optional
        The number of automatically created levels in the contour plot (default: 25).
    colormap : matplotlib.colors.colormap, optional
        A colormap to define the color transitions (default: a blue-white-red colormap).
    norm : matplotlib.colors.norm, optional
        A norm to define the min and max values. If 'None', values from -10 to 10 are assumed (default: None).
    ticks : array([ints]), optional
        An array with values to define the ticks on the colorbar. If 'None' 3 ticks at -10, 0 and 10
        are displayed (default: None).
    annotate : Boolean, optional
        Flag to switch channel annotations on or off (default: True).
    position : [x, y, width, height], optional
        A Rectangle that limits the plot to its boundaries (default: None).

    Returns
    -------
    ((Matplotlib.Axes, Matplotlib.Axes), [Matplotlib.Axes])
        Returns a tuple of first a tuple with the plotted scalp and its colorbar, then a list of all on top
        plotted timeintervals.
    """
    rect_scalp = [.05, .05, .8, .9]
    rect_colorbar = [.9, .05, .05, .9]

    plt.figure(figsize=[16, 13])

    if position is None:
        pos_scalp = rect_scalp
        pos_colorbar = rect_colorbar
    else:
        pos_scalp = _transform_rect(position, rect_scalp)
        pos_colorbar = _transform_rect(position, rect_colorbar)

    #index_v = np.where(data.axes[0] == time)
    #v = data.data[index_v[0][0]]
    #channels = data.axes[1]

    if colormap is None:
        colormap = bwr_cmap()
    if norm is None:
        norm = colors.Normalize(vmin=-10, vmax=10, clip=False)
    if ticks is None:
        ticks = np.linspace(-10.0, 10.0, 3, endpoint=True)

    ax0 = _subplot_scalp(v, chans, position=pos_scalp, levels=levels, annotate=annotate)
    ax1 = _subplot_colorbar(position=pos_colorbar, colormap=colormap, ticks=ticks, norm=norm)

    # adding the timeinterval plots
    s = _get_system()

    tis = []
    for c in data.axes[1]:
        if c in s:

            # generating the channel position on the scalp
            channelpos = tts.channels[c]
            points = calculate_stereographic_projection(channelpos)

            # dirty: these are the x and y limits of the scalp axes
            minx = -1.15
            maxx = 1.15
            miny = -1.10
            maxy = 1.15

            # transformation of karth. to relative coordinates
            xy = (points[0] + (np.abs(minx))) * (1 / (np.abs(minx) + maxx)), \
                 (points[1] + (np.abs(miny))) * (1 / (np.abs(miny) + maxy))

            pos_c = [xy[0] - (scale_ti / 2), xy[1] - (scale_ti / 2), scale_ti, scale_ti]

            # transformation to fit into the scalp part of the plot
            pos_c = _transform_rect(pos_scalp, pos_c)

            tis.append(_subplot_timeinterval(data, position=pos_c, epoch=-1, highlights=None, legend=False,
                                             channel=np.where(data.axes[1] == c)[0][0], shareaxis=None))

            # strip down the timeinterval plots
        else:
            print('The channel "' + c + '" was not found in the tenten-system.')

    return (ax0, ax1), tis


def _subplot_colorbar(position, colormap=bwr_cmap(), ticks=None, norm=None):
    fig = plt.gcf()
    ax = fig.add_axes(position)
    colorbar.ColorbarBase(ax, cmap=colormap, orientation='vertical', ticks=ticks, norm=norm)
    return ax


def _subplot_scalp(v, channels, position, levels=25, colormap=None, annotate=True, norm=None):
    fig = plt.gcf()
    ax = fig.add_axes(position)
    channelpos = [tts.channels[c] for c in channels]
    points = [calculate_stereographic_projection(i) for i in channelpos]
    x = [i[0] for i in points]
    y = [i[1] for i in points]
    z = v
    xx, yy, zz = interpolate_2d(x, y, z)

    if colormap is None:
        colormap = bwr_cmap()

    ax.contourf(xx, yy, zz, levels, zorder=1, cmap=colormap, norm=norm)
    ax.contour(xx, yy, zz, levels, zorder=1, colors="k", norm=norm, linewidths=.1)

    ax.add_artist(plt.Circle((0, 0), radius=1, linewidth=3, fill=False))

    # add a nose
    ax.plot([-0.1, 0], [0.99, 1.1], 'k-', lw=2)
    ax.plot([0.1, 0], [0.99, 1.1], 'k-', lw=2)

    # add ears
    vertsr = [
        (0.99, 0.13),  # P0
        (1.10, 0.3),  # P1
        (1.10, -0.3),  # P2
        (0.99, -0.13)]  # P3

    vertsl = [
        (-0.99, 0.13),  # P0
        (-1.10, 0.3),  # P1
        (-1.10, -0.3),  # P2
        (-0.99, -0.13)]  # P3

    # in combination with Path this creates a bezier-curve with 2 fix-points and 2 control-points
    codes = [Path.MOVETO,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4]

    pathr = Path(vertsr, codes)
    pathl = Path(vertsl, codes)
    patchr = patches.PathPatch(pathr, facecolor='none', lw=2)
    patchl = patches.PathPatch(pathl, facecolor='none', lw=2)
    ax.add_patch(patchr)
    ax.add_patch(patchl)

    # add markers at channels positions
    ax.plot(x, y, 'k+', ms=8, mew=1.2)

    # set the axes limits, so the figure is centered on the scalp
    ax.set_ylim([-1.05, 1.15])
    ax.set_xlim([-1.15, 1.15])

    # hide the axes
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    if annotate:
        for i in zip(channels, zip(x, y)):
            ax.annotate(" " + i[0], i[1])

    return ax


def _subplot_timeinterval(data, position, epoch, highlights=None, hcolors=None,
                          labels=True, legend=True, channel=None, shareaxis=None):
    fig = plt.gcf()

    if shareaxis is None:
        ax = fig.add_axes(position)
    else:
        ax = axes.Axes(fig, position, sharex=shareaxis, sharey=shareaxis)
        fig.add_axes(ax)

    # epoch is -1 when there are no epochs
    if epoch == -1:
        if channel is None:
            ax.plot(data.axes[0], data.data)
        else:
            ax.plot(data.axes[0], data.data[:, channel])
    else:
        if channel is None:
            ax.plot(data.axes[len(data.axes) - 2], data.data[epoch])
        else:
            ax.plot(data.axes[len(data.axes) - 2], data.data[epoch, channel])

    # plotting of highlights
    if highlights is not None:
        set_highlights(highlights, hcolors=hcolors, set_axes=[ax])

    # labeling of axes
    if labels:
        set_labels(data.units[0], "$\mu$V", draw=False, set_axes=[ax])

    # labeling of channels
    if legend:
        if channel is None:
            ax.legend(data.axes[len(data.axes) - 1])
        else:
            ax.legend([data.axes[len(data.axes) - 1][channel]])

    ax.grid(True)
    return ax


def _subplot_r_square(data, position):
    fig = plt.gcf()
    ax = fig.add_axes(position)
    data = np.tile(data, (1, 1))
    ax.imshow(data, aspect='auto', interpolation='none')
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    return ax


def _subplot_scale(xvalue, yvalue, position):
    fig = plt.gcf()
    ax = fig.add_axes(position)
    for item in [fig, ax]:
        item.patch.set_visible(False)
    ax.axis('off')
    ax.add_patch(Rectangle((1, 1), 3, .2, color='black'))
    ax.add_patch(Rectangle((1, 1), .1, 2, color='black'))
    plt.text(1.5, 2, yvalue)
    plt.text(1.5, .25, xvalue)
    ax.set_ylim([0, 4])
    ax.set_xlim([0, 5])
    return ax


def calc_grid(cols, rows, hpad=.05, vpad=.05):
    """
    Calculates a grid of Rectangles and their positions.

    Parameters
    ----------
    cols : int
        The number of desired columns.
    rows : int
        The number of desired rows.
    hpad : float, optional
        The amount of horizontal padding (default: 0.05).
    vpad : float, optional
        The amount of vertical padding (default: 0.05).

    Returns
    -------
    [[float, float, float, float]]
        A list of all rectangle positions in the form of [xi, xy, width, height] sorted from top left to bottom right.
    """
    w = (1 - ((cols + 1) * hpad)) / cols
    h = (1 - ((rows + 1) * vpad)) / rows

    grid = []
    for i in range(cols):
        for j in range(rows):
            xi = ((i % cols + 1) * hpad) + (i % cols * w)
            yj = 1 - (((j % rows + 1) * vpad) + ((j % rows + 1) * h))
            grid.append([xi, yj, w, h])

    return grid


def calc_centered_grid(cols_list, hpad=.05, vpad=.05):
    """
    Calculates a centered grid of Rectangles and their positions.

    Parameters
    ----------
    cols_list : [int]
        List of ints. Every entry represents a row with as many channels as the value.
    hpad : float, optional
        The amount of horizontal padding (default: 0.05).
    vpad : float, optional
        The amount of vertical padding (default: 0.05).

    Returns
    -------
    [[float, float, float, float]]
        A list of all rectangle positions in the form of [xi, xy, width, height] sorted from top left to bottom right.
    """
    h = (1 - ((len(cols_list) + 1) * vpad)) / len(cols_list)
    w = (1 - ((max(cols_list) + 1) * hpad)) / max(cols_list)
    grid = []
    row = 1
    for l in cols_list:
        yi = 1 - ((row * vpad) + (row * h))
        for i in range(l):
            # calculate margin on both sides
            m = .5 - (((l * w) + ((l - 1) * hpad)) / 2)
            xi = m + (i * hpad) + (i * w)
            grid.append([xi, yi, w, h])
        row += 1
    return grid


def _transform_rect(rect, template):
    assert len(rect) == len(template) == 4
    x = rect[0] + (template[0] * rect[2])
    y = rect[1] + (template[1] * rect[3])
    w = rect[2] * template[2]
    h = rect[3] * template[3]
    return [x, y, w, h]


def _get_system():
    system = {
        'Fpz': (0.0, 4.0),
        'Fp1': (-4.0, 3.5),
        'AFp1': (-1.5, 3.5),
        'AFp2': (1.5, 3.5),
        'Fp2': (4.0, 3.5),
        'AF7': (-4.0, 3.0),
        'AF5': (-3.0, 3.0),
        'AF3': (-2.0, 3.0),
        'AFz': (0.0, 3.0),
        'AF4': (2.0, 3.0),
        'AF6': (3.0, 3.0),
        'AF8': (4.0, 3.0),
        'FAF5': (-2.5, 2.5),
        'FAF1': (-0.65, 2.5),
        'FAF2': (0.65, 2.5),
        'FAF6': (2.5, 2.5),
        'F9': (-5.0, 2.0),
        'F7': (-4.0, 2.0),
        'F5': (-3.0, 2.0),
        'F3': (-2.0, 2.0),
        'F1': (-1.0, 2.0),
        'Fz': (0.0, 2.0),
        'F2': (1.0, 2.0),
        'F4': (2.0, 2.0),
        'F6': (3.0, 2.0),
        'F8': (4.0, 2.0),
        'F10': (5.0, 2.0),
        'FFC9': (-4.5, 1.5),
        'FFC7': (-3.5, 1.5),
        'FFC5': (-2.5, 1.5),
        'FFC3': (-1.5, 1.5),
        'FFC1': (-0.5, 1.5),
        'FFC2': (0.5, 1.5),
        'FFC4': (1.5, 1.5),
        'FFC6': (2.5, 1.5),
        'FFC8': (3.5, 1.5),
        'FFC10': (4.5, 1.5),
        'FT9': (-5.0, 1.0),
        'FT7': (-4.0, 1.0),
        'FC5': (-3.0, 1.0),
        'FC3': (-2.0, 1.0),
        'FC1': (-1.0, 1.0),
        'FCz': (0.0, 1.0),
        'FC2': (1.0, 1.0),
        'FC4': (2.0, 1.0),
        'FC6': (3.0, 1.0),
        'FT8': (4.0, 1.0),
        'FT10': (5.0, 1.0),
        'CFC9': (-4.5, 0.5),
        'CFC7': (-3.5, 0.5),
        'CFC5': (-2.5, 0.5),
        'CFC3': (-1.5, 0.5),
        'CFC1': (-0.5, 0.5),
        'CFC2': (0.5, 0.5),
        'CFC4': (1.5, 0.5),
        'CFC6': (2.5, 0.5),
        'CFC8': (3.5, 0.5),
        'CFC10': (4.5, 0.5),
        'T9': (-5.0, 0.0),
        'T7': (-4.0, 0.0),
        'C5': (-3.0, 0.0),
        'C3': (-2.0, 0.0),
        'C1': (-1.0, 0.0),
        'Cz': (0.0, 0.0),
        'C2': (1.0, 0.0),
        'C4': (2.0, 0.0),
        'C6': (3.0, 0.0),
        'T8': (4.0, 0.0),
        'T10': (5.0, 0.0),
        'A1': (-5.0, -0.5),
        'CCP7': (-3.5, -0.5),
        'CCP5': (-2.5, -0.5),
        'CCP3': (-1.5, -0.5),
        'CCP1': (-0.5, -0.5),
        'CCP2': (0.5, -0.5),
        'CCP4': (1.5, -0.5),
        'CCP6': (2.5, -0.5),
        'CCP8': (3.5, -0.5),
        'A2': (5.0, -0.5),
        'TP9': (-5.0, -1.0),
        'TP7': (-4.0, -1.0),
        'CP5': (-3.0, -1.0),
        'CP3': (-2.0, -1.0),
        'CP1': (-1.0, -1.0),
        'CPz': (0.0, -1.0),
        'CP2': (1.0, -1.0),
        'CP4': (2.0, -1.0),
        'CP6': (3.0, -1.0),
        'TP8': (4.0, -1.0),
        'TP10': (5.0, -1.0),
        'PCP9': (-4.5, -1.5),
        'PCP7': (-3.5, -1.5),
        'PCP5': (-2.5, -1.5),
        'PCP3': (-1.5, -1.5),
        'PCP1': (-0.5, -1.5),
        'PCP2': (0.5, -1.5),
        'PCP4': (1.5, -1.5),
        'PCP6': (2.5, -1.5),
        'PCP8': (3.5, -1.5),
        'PCP10': (4.5, -1.5),
        'P9': (-5.0, -2.0),
        'P7': (-4.0, -2.0),
        'P5': (-3.0, -2.0),
        'P3': (-2.0, -2.0),
        'P1': (-1.0, -2.0),
        'Pz': (0.0, -2.0),
        'P2': (1.0, -2.0),
        'P4': (2.0, -2.0),
        'P6': (3.0, -2.0),
        'P8': (4.0, -2.0),
        'P10': (5.0, -2.0),
        'PPO7': (-4.5, -2.5),
        'PPO5': (-3.0, -2.5),
        'PPO3': (-2.0, -2.5),
        'PPO1': (-0.65, -2.5),
        'PPO2': (0.65, -2.5),
        'PPO4': (2.0, -2.5),
        'PPO6': (3.0, -2.5),
        'PPO8': (4.5, -2.5),
        'PO9': (-5.5, -2.6),
        'PO7': (-4.0, -3),
        'PO5': (-3.0, -3),
        'PO3': (-2.0, -3),
        'PO1': (-1.0, -3),
        'POz': (0.0, -3),
        'PO2': (1.0, -3),
        'PO4': (2.0, -3),
        'PO6': (3.0, -3),
        'PO8': (4.0, -3),
        'PO10': (5.5, -2.6),
        'OPO1': (-1.5, -3.5),
        'OPO2': (1.5, -3.5),
        'O9': (-6.5, -3.5),
        'O1': (-4.0, -3.5),
        'O2': (4.0, -3.5),
        'O10': (6.5, -3.5),
        'Oz': (0.0, -4.0),
        'OI1': (1.5, -4.5),
        'OI2': (-1.5, -4.5),
        'I1': (1.0, -5),
        'Iz': (0.0, -5),
        'I2': (-1, -5)}
    return system


def set_highlights(highlights, hcolors=None, set_axes=None):
    """Sets highlights in form of vertical boxes to an axes

    Parameters
    ----------
    highlights : [(start, end)]
        List of tuples containing the start point (included) and end point
        (excluded) of each area to be highlighted.
    hcolors : [colors], optional
        A list of colors to use for the highlights areas.
    set_axes : [matplotlib.Axes], optional
        List of axes to highlights (default: None, all axes of the current
        figure will be highlighted).
    """
    if highlights is not None:

        if set_axes is None:
            set_axes = plt.gcf().axes

        def highlight(start, end, axis, color, alpha):
            axis.axvspan(start, end, edgecolor='w', facecolor=color, alpha=alpha)
            # the edges of the box are at the moment white. transparent edges
            # would be better.

        if hcolors is None:
            hcolors = ['b', 'g', 'r', 'c', 'm', 'y']

        # create a colormask containing #spans colors iterating over specified
        # colors or a standard variety
        colormask = []
        for index, span in enumerate(highlights):
            colormask.append(hcolors[index % len(hcolors)])

        # check if highlights is an instance of the Highlight class
        for p in set_axes:
            for span in highlights:
                highlight(span[0], span[1]-1, p, colormask.pop(0), .5)


def set_labels(xlabel, ylabel, set_axes=None, draw=True):
    """Sets the labels of x- and y-axis of specified axes.

    Parameters
    ----------
    xlabel : String
        The String to label the x-axis.
    ylabel : String
        The String to label the y-axis.
    set_axes : [Matplotlib.Axes], optional
        List of axes to apply the labels to (default: None, the labels are
        applied to all axes of the current figure).
    draw : Boolean, optional
        A flag to switch if the new labels should be directly drawn to the
        plot (default: True).
    """
    if set_axes is None:
        set_axes = plt.gcf().axes

    # labeling of axes
    for ax in set_axes:
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel, rotation=0)

    if draw:
        plt.draw()