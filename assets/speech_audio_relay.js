export default function({data, setTriggerValue}) {
  const state=window.__gsaiAudioRelay || (window.__gsaiAudioRelay={pending:null,last:''});
  function connect(){
    const engine=window.GSAISpeech;if(!engine)return;
    engine.remoteAudio=(text,lang)=>new Promise((resolve,reject)=>{
      if(state.pending){clearTimeout(state.pending.timer);state.pending.reject(Error('Đã thay yêu cầu đọc.'));}
      const id=Date.now().toString(36)+'_'+Math.random().toString(36).slice(2);
      state.pending={id,resolve,reject,timer:setTimeout(()=>{if(state.pending?.id===id){state.pending=null;reject(Error('Dịch vụ giọng đọc hết thời gian chờ.'));}},30000)};
      setTriggerValue('request',{id,text,lang,context:data.context,consent:true});
    });
  }
  connect();
  const observer=new MutationObserver(connect);
  observer.observe(document.body,{childList:true,subtree:true});
  const response=data.response;
  if(response?.id && response.id!==state.last){
    state.last=response.id;
    if(state.pending?.id===response.id){const request=state.pending;state.pending=null;clearTimeout(request.timer);
      if(response.error)request.reject(Error(response.error));else request.resolve(response.audio);}
  }
  return ()=>observer.disconnect();
}
