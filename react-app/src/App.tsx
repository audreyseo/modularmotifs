import React from 'react';
import logo from './logo.svg';
import './App.css';
import GridCanvas from "./GridCanvas"
// import MotifImage from './ui/MotifImage';
// import MotifLibrary from './ui/MotifLibrary';

function App() {
  return (
    <div style={{position: "relative"}}>
    <h1>Grid Canvas</h1>
    <GridCanvas gridSize={40} numRows={15} numCols={15} />
    
      {/* <MotifImage></MotifImage> */}
  </div>
    // <div className="App">
    //   <header className="App-header">
    //     <img src={logo} className="App-logo" alt="logo" />
    //     <p>
    //       Edit <code>src/App.tsx</code> and save to reload.
    //     </p>
    //     <a
    //       className="App-link"
    //       href="https://reactjs.org"
    //       target="_blank"
    //       rel="noopener noreferrer"
    //     >
    //       Learn React
    //     </a>
    //   </header>
    // </div>
  );
}

export default App;
