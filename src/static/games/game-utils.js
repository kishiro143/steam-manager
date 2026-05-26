(function(){
  window.createGameShell=function({instructions}){
    const area=document.getElementById('area');
    area.innerHTML=`<div class="panel"><p>${instructions}</p><p id="stateLabel">Estado: listo (inicio pendiente)</p><p id="scoreLabel">Progreso: 0</p><p id="feedback"></p><div id="controls" class="row"></div><button id="restartBtn">Reiniciar partida</button><div id="board" class="panel"></div></div>`;
    return {
      stateLabel:document.getElementById('stateLabel'),scoreLabel:document.getElementById('scoreLabel'),feedback:document.getElementById('feedback'),controls:document.getElementById('controls'),board:document.getElementById('board'),restartBtn:document.getElementById('restartBtn')
    };
  }
})();
