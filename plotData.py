import numpy as np
import plotly.express as px
import plotly.graph_objects as go



# ============================================================================ #
#                               P L O T   M A P                                #
# ============================================================================ #
def plotMap(self, module, maptype):
    # Plot all spaxels, or only those in Voronoi-region
    if self.restrict2voronoi == 2:
        idxMap = np.where( self.table.BIN_ID >= 0 )[0]
    else:
        idxMap = np.arange( len(self.table.BIN_ID) )

    self.currentMapQuantity = maptype

    # Voronoi table
    if module == 'TABLE':
        val = self.table[maptype][idxMap]
        if maptype == 'FLUX': val = np.log10(val)

    # Masking
    if module == 'MASK':
        val = self.Mask[maptype][idxMap]

    # stellarKinematics
    if module == 'KIN':
        val = self.kinResults[maptype][idxMap]

    # emissionLines
    if module == 'GAS':
        val = self.gasResults[maptype][idxMap]

        try:
            idx_AoNThreshold = np.where( self.gasResults[maptype.split('_')[0]+'_'+maptype.split('_')[1]+'_AON'][idxMap] < self.AoNThreshold )[0]
            val[idx_AoNThreshold] = np.nan
        except:
            print("WARNING: No AoN threshold is applied to the displayed map of "+maptype)

    # starFormationHistories
    if module == 'SFH':
        if maptype.split('_')[-1] == 'DIFF':
            val = self.kinResults[maptype.split('_')[0]][idxMap] - self.sfhResults[maptype.split('_')[0]][idxMap]
        else:
            val = self.sfhResults[maptype][idxMap]

    # lineStrengths
    if module == 'LS':
        val = self.lsResults[maptype][idxMap]



    # Create image in pixels
    xmin = np.nanmin(self.table.X[idxMap])-1;  xmax = np.nanmax(self.table.X[idxMap])+1
    ymin = np.nanmin(self.table.Y[idxMap])-1;  ymax = np.nanmax(self.table.Y[idxMap])+1
    npixels_x = int( np.round( (xmax - xmin)/self.pixelsize ) + 1 )
    npixels_y = int( np.round( (ymax - ymin)/self.pixelsize ) + 1 )
    i = np.array( np.round( (self.table.X[idxMap] - xmin)/self.pixelsize ), dtype=int )
    j = np.array( np.round( (self.table.Y[idxMap] - ymin)/self.pixelsize ), dtype=int )
    image = np.full( (npixels_x, npixels_y), np.nan )
    image[i,j] = val

    # Define special labels
    if   maptype == 'FLUX':    clabel="log( Flux )"  ; cmap='plasma'
    elif maptype == 'V':       clabel="v [km/s]"     ; cmap='RdBu'
    elif maptype == 'SIGMA':   clabel="sigma [km/s]" ; cmap='RdBu'
    elif maptype == 'AGE':     clabel="Age [Gyr]"    ; cmap='plasma'
    elif maptype == 'METALS':  clabel="[M/H]"        ; cmap='plasma'
    elif maptype == 'ALPHA':   clabel="[Mg/Fe]"      ; cmap='plasma'
    else:                      clabel=maptype        ; cmap='plasma'

    x = np.arange(xmin, xmax, self.pixelsize)
    y = np.arange(ymin, ymax, self.pixelsize)
    fig = px.imshow(np.rot90(image)[::-1],
                    x=x,
                    y=y,
                    labels={'x': 'x [arcsec]', 'y':'y [arcsec]', 'color': clabel},
                    color_continuous_scale=cmap)
    fig.update_yaxes(autorange=True)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    return fig


# ============================================================================ #
#                              P L O T   D A T A                               #
# ============================================================================ #
def plotSpectraKIN(self, spectra, bestfit, goodpix):
    # Compile information on masked regions
    masked = np.flatnonzero( np.abs(np.diff(goodpix)) > 1)
    vlines = []
    for i in masked:
        vlines.append( goodpix[i]+1 )
        vlines.append( goodpix[i+1]-1 )
    vlines = np.array(vlines)

    # Clear panels
    # self.axes[panel].cla()

    # Offset of residuals
    offset = np.min(bestfit[:]) - (np.max(bestfit[:]) - np.min(bestfit[:]))*0.10

    # Plot spectra
    idxMin = np.where( self.Lambda == self.kinLambda[0]  )[0][0]
    idxMax = np.where( self.Lambda == self.kinLambda[-1] )[0][0]
    idxLam = np.arange(idxMin, idxMax+1)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=self.LambdaLIN[idxLam], y=spectra[idxLam],
                             name='Spectrum', mode='lines', line=dict(color='black',     width=2)))
    fig.add_trace(go.Scatter(x=self.kinLambdaLIN,      y=bestfit[:],
                             name='Bestfit',  mode='lines', line=dict(color='crimson',   width=2)))
    fig.add_trace(go.Scatter(x=self.kinLambdaLIN,      y=spectra[idxLam] - bestfit + offset,
                             name='Residual', mode='lines', line=dict(color='limegreen', width=2)))

    # Highlight masked regions
    i = 0
    while i < len(vlines)-1:
        badpix = np.arange(vlines[i],vlines[i+1]+1)
        i += 2
    fig.add_trace(go.Scatter(x=[self.LambdaLIN[idxLam][0], self.LambdaLIN[idxLam][-1]], y=[offset,offset],
                             name=None, mode='lines', line=dict(color='black',     width=1)))
    for i in range( len(np.where(vlines != 0)[0]) ):
        if i%2 == 0:
            # self.axes[panel].axvspan(self.Lambda[idxLam][vlines[i]], self.Lambda[idxLam][vlines[i+1]], color='k', alpha=0.1, lw=0)
            fig.add_vrect(x0=self.LambdaLIN[idxLam][vlines[i]], x1=self.LambdaLIN[idxLam][vlines[i+1]], line_width=0, fillcolor="grey", opacity=0.1)
    fig.update_layout(xaxis=dict(range=[self.LambdaLIN[idxLam][0], self.LambdaLIN[idxLam][-1]]),
                      xaxis_title='Wavelength (Angstrom)', yaxis_title='Flux', showlegend=False,
                      margin=dict(l=0, r=0, t=0, b=0))

    return fig


def plotSpectraGAS(self, spectra, bestfit, goodpix):

    # Compile information on masked regions
    masked = np.flatnonzero( np.abs(np.diff(goodpix)) > 1)
    vlines = []
    for i in masked:
        vlines.append( goodpix[i]+1 )
        vlines.append( goodpix[i+1]-1 )
    vlines = np.array(vlines)

    # Clear panels
    # self.axes[panel].cla()

    # Offset of residuals
    offset = np.min(bestfit[:]) - (np.max(bestfit[:]) - np.min(bestfit[:]))*0.10

    # Plot spectra
    idxMin = np.where( self.Lambda == self.gasLambda[0]  )[0]
    idxMax = np.where( self.Lambda == self.gasLambda[-1] )[0]
    idxLam = np.arange(idxMin, idxMax+1)

    fig = go.Figure()
    if self.gasLevel == 'BIN':
        fig.add_trace(go.Scatter(x=self.gasLambdaLIN, y=self.EmissionSubtractedSpectraBIN[self.idxBinShort,:],
                             name='gasLevelBIN', mode='lines', line=dict(color='orange',     width=2)))
        # self.axes[panel].plot(self.gasLambda, self.EmissionSubtractedSpectraBIN[self.idxBinShort,:], color='orange', linewidth=2)
    elif self.gasLevel == 'SPAXEL':
        fig.add_trace(go.Scatter(x=self.gasLambdaLIN, y=self.EmissionSubtractedSpectraSPAXEL[self.idxBinLong,:],
                             name='gasLevelSPAXEL', mode='lines', line=dict(color='orange',     width=2)))
        # self.axes[panel].plot(self.gasLambda, self.EmissionSubtractedSpectraSPAXEL[self.idxBinLong,:], color='orange', linewidth=2)

    # self.axes[panel].plot(self.Lambda[idxLam], spectra[idxLam],               color='k',         linewidth=2)
    # self.axes[panel].plot(self.gasLambda, bestfit[:],                         color='crimson',   linewidth=2)
    # self.axes[panel].plot(self.gasLambda, spectra[idxLam] - bestfit + offset, color='limegreen', linewidth=2)
    fig.add_trace(go.Scatter(x=self.LambdaLIN[idxLam], y=spectra[idxLam],
                 name='Spectrum', mode='lines', line=dict(color='black',     width=2)))
    fig.add_trace(go.Scatter(x=self.gasLambdaLIN, y=bestfit[:],
                 name='Bestfit', mode='lines', line=dict(color='crimson',     width=2)))
    fig.add_trace(go.Scatter(x=self.gasLambdaLIN, y=spectra[idxLam] - bestfit + offset,
                 name='Residual', mode='lines', line=dict(color='limegreen',     width=2)))

    # Highlight masked regions
    i = 0
    while i < len(vlines)-1:
        badpix = np.arange(vlines[i],vlines[i+1]+1)
        i += 2
    # self.axes[panel].plot( [self.Lambda[idxLam][0], self.Lambda[idxLam][-1]], [offset,offset], color='k', linewidth=0.5 )
    fig.add_trace(go.Scatter(x=[self.LambdaLIN[idxLam][0], self.LambdaLIN[idxLam][-1]], y=[offset,offset],
                         name=None, mode='lines', line=dict(color='black',     width=1)))
    for i in range( len(np.where(vlines != 0)[0]) ):
        if i%2 == 0:
            # self.axes[panel].axvspan(self.Lambda[idxLam][vlines[i]], self.Lambda[idxLam][vlines[i+1]], color='k', alpha=0.1, lw=0)
            fig.add_vrect(x0=self.LambdaLIN[idxLam][vlines[i]], x1=self.LambdaLIN[idxLam][vlines[i+1]], line_width=0, fillcolor="grey", opacity=0.1)
    fig.update_layout(xaxis=dict(range=[self.LambdaLIN[idxLam][0], self.LambdaLIN[idxLam][-1]]),
                      xaxis_title='Wavelength (Angstrom)', yaxis_title='Flux', showlegend=False,
                      margin=dict(l=0, r=0, t=0, b=0))
    # self.axes[panel].set_xlim([self.Lambda[idxLam][0], self.Lambda[idxLam][-1]])
    # self.axes[panel].set_ylabel('Flux')
    #
    # ticks = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format( np.exp(x) ))
    # self.axes[panel].xaxis.set_major_formatter(ticks)
    return fig


def plotSpectraSFH(self, spectra, bestfit, goodpix):

    # Compile information on masked regions
    masked = np.flatnonzero( np.abs(np.diff(goodpix)) > 1)
    vlines = []
    for i in masked:
        vlines.append( goodpix[i]+1 )
        vlines.append( goodpix[i+1]-1 )
    vlines = np.array(vlines)

    # Clear panels
    # self.axes[panel].cla()

    # Offset of residuals
    offset = np.min(bestfit[:]) - (np.max(bestfit[:]) - np.min(bestfit[:]))*0.10

    # Plot spectra
    idxMin = np.where( self.Lambda == self.sfhLambda[0]  )[0]
    idxMax = np.where( self.Lambda == self.sfhLambda[-1] )[0]
    idxLam = np.arange(idxMin, idxMax+1)

    fig = go.Figure()
    try:
        idxMin     = np.where( self.gasLambda == self.sfhLambda[0]  )[0]
        idxMax     = np.where( self.gasLambda == self.sfhLambda[-1] )[0]
        idxLamGand = np.arange(idxMin, idxMax+1)
        # self.axes[panel].plot(self.gasLambda[idxLamGand], self.EmissionSubtractedSpectraBIN[self.idxBinShort,idxLamGand],                    color='orange',    linewidth=2)
        # self.axes[panel].plot(self.gasLambda[idxLamGand], self.EmissionSubtractedSpectraBIN[self.idxBinShort,idxLamGand] - bestfit + offset, color='limegreen', linewidth=2)
        fig.add_trace(go.Scatter(x=self.gasLambdaLIN[idxLamGand], y=self.EmissionSubtractedSpectraBIN[self.idxBinShort,idxLamGand],
                     name=None, mode='lines', line=dict(color='orange',     width=2)))
        fig.add_trace(go.Scatter(x=self.gasLambdaLIN[idxLamGand], y=self.EmissionSubtractedSpectraBIN[self.idxBinShort,idxLamGand] - bestfit + offset,
                     name=None, mode='lines', line=dict(color='limegreen',     width=2)))
    except:
        pass

    # self.axes[panel].plot(self.Lambda[idxLam], spectra[idxLam], color='k',       linewidth=2)
    # self.axes[panel].plot(self.sfhLambda,      bestfit[:],      color='crimson', linewidth=2)
    fig.add_trace(go.Scatter(x=self.LambdaLIN[idxLam], y=spectra[idxLam],
                 name='Spectrum', mode='lines', line=dict(color='black',     width=2)))
    fig.add_trace(go.Scatter(x=self.sfhLambdaLIN, y=bestfit[:],
                 name='Bestfit', mode='lines', line=dict(color='crimson',     width=2)))

    # Highlight masked regions
    i = 0
    while i < len(vlines)-1:
        badpix = np.arange(vlines[i],vlines[i+1]+1)
        i += 2
    # self.axes[panel].plot( [self.Lambda[idxLam][0], self.Lambda[idxLam][-1]], [offset,offset], color='k', linewidth=0.5 )
    fig.add_trace(go.Scatter(x=[self.LambdaLIN[idxLam][0], self.LambdaLIN[idxLam][-1]], y=[offset,offset],
                         name=None, mode='lines', line=dict(color='black',     width=1)))
    for i in range( len(np.where(vlines != 0)[0]) ):
        if i%2 == 0:
            # self.axes[panel].axvspan(self.Lambda[idxLam][vlines[i]], self.Lambda[idxLam][vlines[i+1]], color='k', alpha=0.1, lw=0)
            fig.add_vrect(x0=self.LambdaLIN[idxLam][vlines[i]], x1=self.LambdaLIN[idxLam][vlines[i+1]], line_width=0, fillcolor="grey", opacity=0.1)

    # self.axes[panel].set_xlim([self.Lambda[idxLam][0], self.Lambda[idxLam][-1]])
    # self.axes[panel].set_ylabel('Flux')
    fig.update_layout(xaxis=dict(range=[self.LambdaLIN[idxLam][0], self.LambdaLIN[idxLam][-1]]),
                      xaxis_title='Wavelength (Angstrom)', yaxis_title='Flux', showlegend=False,
                      margin=dict(l=0, r=0, t=0, b=0))
    # ticks = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format( np.exp(x) ))
    # self.axes[panel].xaxis.set_major_formatter(ticks)
    return fig


def plotSFH(self, idxBinShort):
    # Clear panels
    # self.axes[panel].cla()

    # Get star formation history
    collapsed = np.sum( self.Weights, axis=(1,3) )

    # Plot it all
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=self.age, y=collapsed[idxBinShort, :],
                             name='Spectrum', mode='lines', line=dict(width=2)))
    fig.update_layout(xaxis=dict(range=[self.age[0], self.age[-1]]),
                      title={'text': 'Star Formation History; Mean Age: ???',
                             'x': 0.5, 'y':0.99,
                             'xanchor':'center', 'yanchor':'top'},
                      xaxis_title='Age [Gyr]',
                      yaxis_title='#', showlegend=False,
                      margin=dict(l=0, r=0, t=20, b=0))
    return fig

def plotMDF(self, idxBinShort, idx_alpha):
    fig = go.Figure(data=go.Heatmap(x=self.age,
                                    y=self.metals,
                                    z=self.Weights[idxBinShort,:,:,idx_alpha],
                                    type='heatmap',
                                    colorscale='Viridis'))
    fig.update_layout(xaxis_title='Age [Gyr]', yaxis_title='[M/H]', margin=dict(l=0, r=0, t=0, b=0))
    return fig
