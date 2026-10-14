// Gameplay regression fixtures enter a known v2 save explicitly. Production
// boot always goes through the title screen and never skips character selection.
export async function enterGame(page){await page.evaluate(async()=>{const a=globalThis.lpLegend;if(a&&!globalThis.lpLegendError&&a.screen!=='game')await a.startGame(a.platform.load(),{characterId:a.roster.activeId});});}
