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

    x = np.arange(xmin-self.pixelsize/2, xmax+self.pixelsize/2, self.pixelsize)[:npixels_x]
    y = np.arange(ymin-self.pixelsize/2, ymax+self.pixelsize/2, self.pixelsize)[:npixels_y]
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
def plotSpectra(self, idxBinShort, idxBinLong):
    figs = []

    # Plot stellarKinematics fit
    if self.KIN == True:
        fig = plotSpectraKIN(self, self.Spectra[idxBinShort], self.kinBestfit[idxBinShort], self.kinGoodpix)
        if 'V' in self.kinResults.names  and  'SIGMA' in self.kinResults.names  and  'H3' in self.kinResults.names  and  'H4' in self.kinResults.names:
            fig.update_layout(title={'text': "Stellar kinematics: V={:.1f}km/s, SIGMA={:.1f}km/s, H3={:.2f}, H4={:.2f}".format(self.kinResults.V[idxBinLong], self.kinResults.SIGMA[idxBinLong], self.kinResults.H3[idxBinLong], self.kinResults.H4[idxBinLong]),
                                     'x': 0.5, 'y':0.95,
                                     'xanchor':'center', 'yanchor':'top'})
        elif 'V' in self.kinResults.names  and  'SIGMA' in self.kinResults.names:
            fig.update_layout(title={'text': "Stellar kinematics: V={:.1f}km/s, SIGMA={:.1f}km/s".format(self.kinResults.V[idxBinLong], self.kinResults.SIGMA[idxBinLong]),
                                     'x': 0.5, 'y':0.95,
                                     'xanchor':'center', 'yanchor':'top'})
        figs.append(fig)

    # Plot emissionLines fit
    if self.GAS == True:
        if self.gasLevel == 'BIN':
            fig = plotSpectraGAS(self, self.Spectra[idxBinShort], self.gasBestfit[idxBinShort], self.gasGoodpix, idxBinShort, idxBinLong)
        elif self.gasLevel == 'SPAXEL':
            fig = plotSpectraGAS(self, self.AllSpectra[idxBinLong], self.gasBestfit[idxBinLong], self.gasGoodpix, idxBinShort, idxBinLong)
            # self.axes[2].set_title("SPAXEL_ID = {:d}".format(self.idxBinLong), loc='right')
        try:
            line='0' # need to modify for the future
            fig.update_layout(title={'text': "Emission-line kinematics: v={:.1f}km/s, sigma={:.1f}km/s".format(self.gasResults[line+'_V'][idxBinLong], self.gasResults[line+'_S'][idxBinLong]),
                                     'x': 0.5, 'y':0.95,
                                     'xanchor':'center', 'yanchor':'top'})
        except:
            fig.update_layout(title={'text': 'Emission-line analysis',
                                     'x': 0.5, 'y':0.95,
                                     'xanchor':'center', 'yanchor':'top'})
        figs.append(fig)

    # Plot starFormationHistories results
    if self.SFH == True:
        fig = plotSpectraSFH(self, self.Spectra[idxBinShort], self.sfhBestfit[idxBinShort], self.sfhGoodpix)
        fig.update_layout(title={'text': "Stellar populations: Age={:.2f} Gyr, [M/H]={:.2f}, [alpha/Fe]={:.2f}".format(self.sfhResults['AGE'][idxBinLong], self.sfhResults['METAL'][idxBinLong], self.sfhResults['ALPHA'][idxBinLong]),
                                 'x': 0.5, 'y':0.95,
                                 'xanchor':'center', 'yanchor':'top'})
        figs.append(fig)

    return figs


def plotSpectraKIN(self, spectra, bestfit, goodpix):
    # spectra = self.Spectra[idxBinShort]
    # bestfit = self.kinBestfit[idxBinShort]
    # goodpix = self.kinGoodpix

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
                      margin=dict(l=15, r=15, t=35, b=15))

    return fig


def plotSpectraGAS(self, spectra, bestfit, goodpix, idxBinShort, idxBinLong):
    # spectra = self.Spectra[idxBinShort]
    # bestfit = self.gasBestfit[idxBinShort]
    # goodpix = self.kinGoodpix

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
        fig.add_trace(go.Scatter(x=self.gasLambdaLIN, y=self.EmissionSubtractedSpectraBIN[idxBinShort,:],
                             name='gasLevelBIN', mode='lines', line=dict(color='orange',     width=2)))
        # self.axes[panel].plot(self.gasLambda, self.EmissionSubtractedSpectraBIN[self.idxBinShort,:], color='orange', linewidth=2)
    elif self.gasLevel == 'SPAXEL':
        fig.add_trace(go.Scatter(x=self.gasLambdaLIN, y=self.EmissionSubtractedSpectraSPAXEL[idxBinLong,:],
                             name='gasLevelSPAXEL', mode='lines', line=dict(color='orange',     width=2)))
        # self.axes[panel].plot(self.gasLambda, self.EmissionSubtractedSpectraSPAXEL[idxBinLong,:], color='orange', linewidth=2)

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
                      margin=dict(l=15, r=15, t=35, b=15))

    # self.axes[panel].set_xlim([self.Lambda[idxLam][0], self.Lambda[idxLam][-1]])
    # self.axes[panel].set_ylabel('Flux')
    #
    # ticks = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format( np.exp(x) ))
    # self.axes[panel].xaxis.set_major_formatter(ticks)
    return fig


def plotSpectraSFH(self, spectra, bestfit, goodpix):
    # spectra = self.Spectra[idxBinShort]
    # bestfit = self.sfhBestfit[idxBinShort]
    # goodpix = self.kinGoodpix

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
        fig.add_trace(go.Scatter(x=self.gasLambdaLIN[idxLamGand], y=self.EmissionSubtractedSpectraBIN[idxBinShort,idxLamGand],
                     name=None, mode='lines', line=dict(color='orange',     width=2)))
        fig.add_trace(go.Scatter(x=self.gasLambdaLIN[idxLamGand], y=self.EmissionSubtractedSpectraBIN[idxBinShort,idxLamGand] - bestfit + offset,
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
                      margin=dict(l=15, r=15, t=35, b=15))
    # ticks = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format( np.exp(x) ))
    # self.axes[panel].xaxis.set_major_formatter(ticks)
    return fig


def plotSFH(self, idxBinShort, idxBinLong):
    # Clear panels
    # self.axes[panel].cla()

    # Get star formation history
    collapsed = np.sum( self.Weights, axis=(1,3) )

    # Plot it all
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=self.age, y=collapsed[idxBinShort, :],
                             name='Spectrum', mode='lines', line=dict(width=2)))
    fig.update_layout(xaxis=dict(range=[self.age[0], self.age[-1]]),
                      xaxis_title='Age [Gyr]',
                      yaxis_title='#', showlegend=False,
                      margin=dict(l=15, r=15, t=35, b=15))
    fig.update_layout(title={'text': "Star Formation History; Mean Age: {:.2f}".format(self.sfhResults['AGE'][idxBinLong])+" Gyr",
                             'x': 0.5, 'y':0.95,
                             'xanchor':'center', 'yanchor':'top'})
    return fig

def plotMDF(self, idxBinShort):
    fig1 = go.Figure(data=go.Heatmap(x=self.age,
                                    y=self.metals,
                                    z=self.Weights[idxBinShort,:,:,0],
                                    type='heatmap',
                                    colorscale='Viridis'))
    fig1.update_layout(xaxis_title='Age [Gyr]', yaxis_title='[M/H]', margin=dict(l=15, r=15, t=35, b=15))
    fig1.update_layout(title={'text': "Mass Fraction - [alpha/Fe]=0.00",
                     'x': 0.5, 'y':0.95,
                     'xanchor':'center', 'yanchor':'top'})
    figs = [fig1]

    if self.Weights.shape[3] == 2:
        fig2 = go.Figure(data=go.Heatmap(x=self.age,
                                        y=self.metals,
                                        z=self.Weights[idxBinShort,:,:,1],
                                        type='heatmap',
                                        colorscale='Viridis'))
        fig2.update_layout(xaxis_title='Age [Gyr]', yaxis_title='[M/H]', margin=dict(l=15, r=15, t=35, b=15))
        fig2.update_layout(title={'text': "Mass Fraction - [alpha/Fe]=0.40",
                         'x': 0.5, 'y':0.95,
                         'xanchor':'center', 'yanchor':'top'})
        figs.append(fig2)

    return figs
