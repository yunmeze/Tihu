// Decode native sheets before they enter a draw call. ImageBitmap avoids the
// HTML image's deferred decode/conversion on first texSubImage2D upload.
export async function browserImage(file){
 if(typeof createImageBitmap==='function'){
  const response=await fetch(file);if(!response.ok)throw Error(file+' '+response.status);
  const blob=await response.blob();
  try{return await createImageBitmap(blob,{imageOrientation:'none',premultiplyAlpha:'none',colorSpaceConversion:'none'});}catch{/* Older browsers can still use the decoded image path below. */}
 }
 const image=await new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>reject(Error(file));im.src=file;});
 if(image.decode)await image.decode();return image;
}
