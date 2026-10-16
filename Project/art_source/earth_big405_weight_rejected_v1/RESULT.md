# Big405 generated weight-control attempt: reject direct data use

One attempt returned1536x1024RGB, exact3:2 andopaque. Leftsoil/rightgrass broad direction is present, but output fails strict neutralgray requirement and does not establish credible source-derived intermediatecoverage. It must not be silently decoded into a productionweight.

## Actual chain
One complete576x384nearest6x source ref, viewed before call. ActualPROMPT.txt,REQUEST_FROZEN.json,INPUT_SHA256.json frozen. RAW.png bytecopy from generated_images/exec-f2202f31-9ce6-42d1-9c0d-f98dac46d44a.png;SHA953c750f09ebfbc5d494cccc8164a82d42af5427a2360eefd9bc8401af64295a. No otherrefs. WholewindowLANCZOS displays96x64/192x128/576x384 only; rawRGB remainsunchanged. No grayscaleconversion,channelpick,autocontrast,normalization,threshold,blurrepair,edgeforcing or sourceoverlay. review.py reproduces readouts;AUDIT.json preserves rawinspection.

## Data gate
Only40.512% of rawpixels haveR=G=B. Maximumchannelspread4,p99spread2. Smalltint doesnotlookstrong but violatesexplicitneutraldata contract. No automaticRGBaverage/luminanceextract.
Leftanchorx0..22: RGBmean(2.837,2.760,2.592),range0..40;exactblack38.924%. Rightanchorx74..95:mean(246.160,245.911,245.923),min(172,170,170),max255;exactwhite0.150%. Thus nearendpoint overallread ispresent but neitheranchor is uniformlypureendpoint. Acrosswholeimage146687exactblackpixels,541exactwhitepixels. Do not describe pureedges from theseregionalaverages or force0/1 afterward.
Centraluncertainband remainsuncertain independently of output. Itsgraymean~119 isnotconfidence anddoesnotcalibrateactualgrassfraction.

## Art/control reading at1x and2x
COMPARE_1X/2X and6X preserve samewindow againstsource. Directionleftdark/rightlight iscorrect. Themiddle isdominatedbyrepeatedbranching/cloudlike-grayblotchesandsoftnestedpatterns. Thislooks like anewdecorativemixingtexture ratherthan aninterpretable low-frequencyboundary withsource-supported sparsegrassincursions. At1xpatternstillreadsasdistinctblobs;6xmerelyrevealsitmoreclearly. Theoutputisnotanobviouscopyofsourcebrightness, butavoidingbrightnesscopy alone isnotaccuratecoverage. No claimsourceislands/top-bottomentrytraces arecorrectlypreserved. Fulloriginaluncertainbandandall8instanceholdsremain.

## Stop
Rejectdirectshader/CPUblendusependingrootreview. No shader, allmapapplication or ownerreplacement. No retry or correctiveimageoperation.405@38,16 remainsHOLD withitsoriginalneighborconflict; thisgeneratedmapdoesnotresolveit. Theattemptshowsa generative grayscale controlrequest canbevisuallyneargrayscale yetfailnumericneutralityandshapeinterpretability. Any futurestrategyrequiresnewexplicitapproval andshouldnotstartbynormalizingthisrawtohidefailure.
