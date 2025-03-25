import React, { useState } from 'react';
import { Stage, Layer, Rect, Line } from 'react-konva';
import Hoverer from './Hoverer'

interface GridCanvasProps {
  gridSize?: number; // Optional prop, defaults to 30
  numRows?: number;  // Optional prop, defaults to 20
  numCols?: number;  // Optional prop, defaults to 20
}

interface AnnotationProp {
  x: number;
  y: number;
  width: number;
  height: number;
  key: string;
}

const GridCanvas: React.FC<GridCanvasProps> = ({
  gridSize = 30,
  numRows = 20,
  numCols = 20,
}) => {

    // State to track the colors of each rectangle (grid cell)
    const [colors, setColors] = useState<string[][]>(
      Array.from({ length: numRows }, () =>
        Array.from({ length: numCols }, () => 'transparent')
      )
    );

    const [newAnnotation, setNewAnnotation] = useState<AnnotationProp[]>([]);

    const [myAnnotation, setAnnotation] = useState<AnnotationProp>({
      x: 0,
      y: 0,
      width: 2,
      height: 2,
      key: ""
    })
  
    // Function to handle rectangle click and change its color
    const handleRectClick = (row: number, col: number) => {
      // Create a copy of the colors state
      const newColors = [...colors];
      // Toggle between white and a new color (e.g., red)
      newColors[row][col] = newColors[row][col] === 'transparent' ? '#FF0000AA' : 'transparent';
      // Update the state with the new colors
      setColors(newColors);
    };

    const handleMouseMove = (event: any) => {
      // if (newAnnotation.length === 0) {
        const { x, y } = event.target.getStage().getPointerPosition();
        // console.log(x, y)
        const x0 = Math.floor(x / gridSize) * gridSize;
        const y0 = Math.floor(y / gridSize) * gridSize;
        setAnnotation({
          x: x0,
          y: y0,
          width: 2,
          height: 2,
          key: "0"
        })
    };

  // Function to generate grid lines
  const generateGridLines = (): { points: number[] }[] => {
    const lines: { points: number[] }[] = [];

    // Horizontal lines
    for (let i = 0; i <= numRows; i++) {
      lines.push({
        points: [0, i * gridSize, numCols * gridSize, i * gridSize],
      });
    }

    // Vertical lines
    for (let i = 0; i <= numCols; i++) {
      lines.push({
        points: [i * gridSize, 0, i * gridSize, numRows * gridSize],
      });
    }

    return lines;
  };


  const motif: string[][] = [["#FFFFFFAA", "#FFFFFFAA"], ["#000000AA", "#000000AA"]];
  

  return (
    <Stage onMouseMove={handleMouseMove} width={numCols * gridSize} height={numRows * gridSize}>
      <Layer>
        {/* Create a grid of rectangles */}
        {Array.from({ length: numRows }).map((_, row) =>
          Array.from({ length: numCols }).map((_, col) => (
            <Rect
              key={`${row}-${col}`}
              x={col * gridSize}
              y={row * gridSize}
              width={gridSize}
              height={gridSize}
              fill={colors[row][col]}  // Set the fill color based on the state
              stroke="black"
              strokeWidth={1}
              onClick={() => handleRectClick(row, col)}  // Handle click to change color
            />
          ))
        )}
      </Layer>
      <Hoverer
        x={myAnnotation.x}
        y={myAnnotation.y}
        colors={motif}
        height={2}
        width={2}
        gridSize={gridSize}
      />
    </Stage>
  );
};

export default GridCanvas;
