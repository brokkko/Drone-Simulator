import './App.css';
import Scene from './Scene'
import {useEffect, useState} from "react";

function App() {


  let socket

  const [state, setState] = useState('no')


  socket = new WebSocket("ws://127.0.0.1:8765");

  socket.onopen = function(e) {
    setState('connected')
  };



  return (
    <div className="App">
      <Scene Socket = {socket}/>
      <h1>{state}</h1>
    </div>
  );
}

export default App;
