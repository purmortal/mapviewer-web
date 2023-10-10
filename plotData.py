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

    # x = np.arange(xmin-self.pixelsize/2, xmax+self.pixelsize/2, self.pixelsize)[:npixels_x]
    # y = np.arange(ymin-self.pixelsize/2, ymax+self.pixelsize/2, self.pixelsize)[:npixels_y]
    x = np.arange(xmin, xmax + self.pixelsize, self.pixelsize)[:npixels_x]
    y = np.arange(ymin, ymax + self.pixelsize, self.pixelsize)[:npixels_y]
    fig = px.imshow(np.rot90(image)[::-1],
                    x=x,
                    y=y,
                    labels={'x': 'x [arcsec]', 'y':'y [arcsec]', 'color': clabel},
                    color_continuous_scale=cmap)

    if hasattr(self, 'idxBinShort') == True:
        fig.add_trace(go.Scatter(x=[self.table.XBIN[self.table['BIN_ID']==self.idxBinShort][0]], y=[self.table.YBIN[self.table['BIN_ID']==self.idxBinShort][0]], opacity=0.6,
                                 mode='markers', name='VorBin', marker=dict(symbol='x', line_width=0.8, line_color='white', color='black', size=8)))
    if hasattr(self, 'idxBinLong') == True:
        if self.idxBinLong != None:
            fig.add_trace(go.Scatter(x=[self.table.X[self.idxBinLong]], y=[self.table.Y[self.idxBinLong]], opacity=0.6,
                                     mode='markers', name='SpaxelBin', marker=dict(symbol='circle', line_width=0.8, line_color='white', color='black', size=8)))

    fig.update_yaxes(autorange=True)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False, hoverdistance=2)
    # fig.update_layout(coloraxis_colorbar_x=-0.1)

    self.plotMap = fig

    return fig


# ============================================================================ #
#                              P L O T   D A T A                               #
# ============================================================================ #
def plotSpectra(self):
    figs = []

    # Plot stellarKinematics fit
    if self.KIN == True:
        fig = plotSpectraKIN(self, self.Spectra[self.idxBinShort], self.kinBestfit[self.idxBinShort], self.kinGoodpix)
        if 'V' in self.kinResults.names  and  'SIGMA' in self.kinResults.names  and  'H3' in self.kinResults.names  and  'H4' in self.kinResults.names:
            fig.update_layout(title={'text': "Stellar kinematics: V={:.1f}km/s, SIGMA={:.1f}km/s, H3={:.2f}, H4={:.2f}".format(self.kinResults_Vorbin.V[self.idxBinShort], self.kinResults_Vorbin.SIGMA[self.idxBinShort], self.kinResults_Vorbin.H3[self.idxBinShort], self.kinResults_Vorbin.H4[self.idxBinShort]),
                                     'x': 0.5, 'y':0.95,
                                     'xanchor':'center', 'yanchor':'top'})
        elif 'V' in self.kinResults.names  and  'SIGMA' in self.kinResults.names:
            fig.update_layout(title={'text': "Stellar kinematics: V={:.1f}km/s, SIGMA={:.1f}km/s".format(self.kinResults_Vorbin.V[self.idxBinShort], self.kinResults_Vorbin.SIGMA[self.idxBinShort]),
                                     'x': 0.5, 'y':0.95,
                                     'xanchor':'center', 'yanchor':'top'})
        figs.append(fig)

    # Plot emissionLines fit
    if self.GAS == True:
        if self.gasLevel == 'BIN':
            fig = plotSpectraGAS(self, self.Spectra[self.idxBinShort], self.gasBestfit[self.idxBinShort], self.gasGoodpix)
        elif self.gasLevel == 'SPAXEL':
            fig = plotSpectraGAS(self, self.AllSpectra[self.idxBinLong], self.gasBestfit[self.idxBinLong], self.gasGoodpix)
            # self.axes[2].set_title("SPAXEL_ID = {:d}".format(self.self.idxBinLong), loc='right')
        try:
            line='0' # need to modify for the future
            fig.update_layout(title={'text': "Emission-line kinematics: v={:.1f}km/s, sigma={:.1f}km/s".format(self.gasResults_Vorbin[line+'_V'][self.idxBinShort], self.gasResults_Vorbin[line+'_S'][self.idxBinShort]),
                                     'x': 0.5, 'y':0.95,
                                     'xanchor':'center', 'yanchor':'top'})
        except:
            fig.update_layout(title={'text': 'Emission-line analysis',
                                     'x': 0.5, 'y':0.95,
                                     'xanchor':'center', 'yanchor':'top'})
        figs.append(fig)

    # Plot starFormationHistories results
    if self.SFH == True:
        fig = plotSpectraSFH(self, self.Spectra[self.idxBinShort], self.sfhBestfit[self.idxBinShort], self.sfhGoodpix)
        fig.update_layout(title={'text': "Stellar populations: Age={:.2f} Gyr, [M/H]={:.2f}, [alpha/Fe]={:.2f}".format(self.sfhResults_Vorbin['AGE'][self.idxBinShort], self.sfhResults_Vorbin['METAL'][self.idxBinShort], self.sfhResults_Vorbin['ALPHA'][self.idxBinShort]),
                                 'x': 0.5, 'y':0.95,
                                 'xanchor':'center', 'yanchor':'top'})
        figs.append(fig)

    return figs


def plotSpectraKIN(self, spectra, bestfit, goodpix):
    # spectra = self.Spectra[self.idxBinShort]
    # bestfit = self.kinBestfit[self.idxBinShort]
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
                      margin=dict(l=3, r=3, t=35, b=3))
    fig.update_layout(hovermode="x unified")

    return fig


def plotSpectraGAS(self, spectra, bestfit, goodpix):
    # spectra = self.Spectra[self.idxBinShort]
    # bestfit = self.gasBestfit[self.idxBinShort]
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
        fig.add_trace(go.Scatter(x=self.gasLambdaLIN, y=self.EmissionSubtractedSpectraBIN[self.idxBinShort,:],
                             name='gasLevelBIN', mode='lines', line=dict(color='orange',     width=2)))
        # self.axes[panel].plot(self.gasLambda, self.EmissionSubtractedSpectraBIN[self.self.idxBinShort,:], color='orange', linewidth=2)
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
                      margin=dict(l=3, r=3, t=35, b=3))
    fig.update_layout(hovermode="x unified")

    # self.axes[panel].set_xlim([self.Lambda[idxLam][0], self.Lambda[idxLam][-1]])
    # self.axes[panel].set_ylabel('Flux')
    #
    # ticks = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format( np.exp(x) ))
    # self.axes[panel].xaxis.set_major_formatter(ticks)
    return fig


def plotSpectraSFH(self, spectra, bestfit, goodpix):
    # spectra = self.Spectra[self.idxBinShort]
    # bestfit = self.sfhBestfit[self.idxBinShort]
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
        # self.axes[panel].plot(self.gasLambda[idxLamGand], self.EmissionSubtractedSpectraBIN[self.self.idxBinShort,idxLamGand],                    color='orange',    linewidth=2)
        # self.axes[panel].plot(self.gasLambda[idxLamGand], self.EmissionSubtractedSpectraBIN[self.self.idxBinShort,idxLamGand] - bestfit + offset, color='limegreen', linewidth=2)
        fig.add_trace(go.Scatter(x=self.gasLambdaLIN[idxLamGand], y=self.EmissionSubtractedSpectraBIN[self.idxBinShort,idxLamGand],
                     name='EmissionSub', mode='lines', line=dict(color='orange',     width=2)))
        fig.add_trace(go.Scatter(x=self.gasLambdaLIN[idxLamGand], y=self.EmissionSubtractedSpectraBIN[self.idxBinShort,idxLamGand] - bestfit + offset,
                     name='Residual', mode='lines', line=dict(color='limegreen',     width=2)))
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
                      margin=dict(l=3, r=3, t=35, b=3))
    fig.update_layout(hovermode="x unified")
    # ticks = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format( np.exp(x) ))
    # self.axes[panel].xaxis.set_major_formatter(ticks)
    return fig


def plotSFH(self):
    # Clear panels
    # self.axes[panel].cla()

    # Get star formation history
    collapsed = np.sum( self.Weights, axis=(1,3) )

    # Plot it all
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=self.age, y=collapsed[self.idxBinShort, :],
                             name='Spectrum', mode='lines', line=dict(width=2)))
    fig.update_layout(xaxis=dict(range=[self.age[0], self.age[-1]]),
                      xaxis_title='Age [Gyr]',
                      yaxis_title='#', showlegend=False,
                      margin=dict(l=3, r=3, t=35, b=3))
    fig.update_layout(title={'text': "Star Formation History; Mean Age: {:.2f}".format(self.sfhResults_Vorbin['AGE'][self.idxBinShort])+" Gyr",
                             'x': 0.5, 'y':0.95,
                             'xanchor':'center', 'yanchor':'top'})
    fig.update_layout(hovermode="x")
    return fig


def plotMDF(self):
    fig1 = go.Figure(data=go.Heatmap(x=self.age,
                                    y=self.metals,
                                    z=self.Weights[self.idxBinShort,:,:,0],
                                    type='heatmap',
                                    colorscale='Viridis'))
    fig1.update_layout(xaxis_title='Age [Gyr]', yaxis_title='[M/H]', margin=dict(l=3, r=3, t=35, b=3))
    fig1.update_layout(title={'text': "Mass Fraction - [alpha/Fe]=0.00",
                     'x': 0.5, 'y':0.95,
                     'xanchor':'center', 'yanchor':'top'})
    figs = [fig1]

    if self.Weights.shape[3] == 2:
        fig2 = go.Figure(data=go.Heatmap(x=self.age,
                                        y=self.metals,
                                        z=self.Weights[self.idxBinShort,:,:,1],
                                        type='heatmap',
                                        colorscale='Viridis'))
        fig2.update_layout(xaxis_title='Age [Gyr]', yaxis_title='[M/H]', margin=dict(l=3, r=3, t=35, b=3))
        fig2.update_layout(title={'text': "Mass Fraction - [alpha/Fe]=0.40",
                         'x': 0.5, 'y':0.95,
                         'xanchor':'center', 'yanchor':'top'})
        figs.append(fig2)

    return figs
