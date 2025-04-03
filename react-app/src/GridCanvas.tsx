import React, { useState } from 'react';
import { Stage, Layer, Rect, Line } from 'react-konva';
import Hoverer from './Hoverer'
import { group } from 'console';
import Motif, {Color} from './core/Motif';
import Design from './core/Design';
import { ReactColorPicker } from 'react-color-picker-tool';
import { SketchPicker } from 'react-color';
import ButtonPicker from './ButtonPicker';
import MotifLibrary from './ui/MotifLibrary';


interface GridCanvasProps {
  gridSize?: number; // Optional prop, defaults to 30
  numRows?: number;  // Optional prop, defaults to 20
  numCols?: number;  // Optional prop, defaults to 20
}

interface AnnotationProp {
  colors: string[][];
  motif: Motif;
  x: number;
  y: number;
  width: number;
  height: number;
  key: string;
}

interface ColorProp {
  r: number;
  g: number;
  b: number;
  a: number;
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
      colors: [["#FFFFFFAA", "#FFFFFFAA"], ["#000000AA", "#000000AA"]],
      motif: new Motif([[Color.FORE, Color.BACK], [Color.BACK, Color.FORE]]),
      x: 0,
      y: 0,
      width: 2,
      height: 2,
      key: ""
    })

    const [chosenMotif, setChosenMotif] = useState<Motif>(new Motif([[Color.FORE, Color.BACK], [Color.BACK, Color.FORE]]));

    const [myDesign, setDesign] = useState<Design>(new Design(numCols, numRows))
    const [color, setColor] = useState<ColorProp>({r: 123, g: 123, b: 123, a: 0.5})
  
    // Function to handle rectangle click and change its color
    const handleRectClick = (row: number, col: number) => {
      // Create a copy of the colors state
      const newColors = [...colors];
      const annotation_colors = myAnnotation.colors
      for (let i = 0; i < myAnnotation.height; i++) {
        for (let j = 0; j < myAnnotation.width; j++) {
          newColors[row + i][col + j] = myAnnotation.colors[i][j]
        }
      }
      const design = myDesign
      design.add_motif(chosenMotif, col, row)
      // Toggle between white and a new color (e.g., red)
      // newColors[row][col] = newColors[row][col] === 'transparent' ? '#FF0000AA' : 'transparent';
      // Update the state with the new colors
      setColors(newColors);
      setDesign(design)
    };

    const handleMouseMove = (event: any) => {
      // if (newAnnotation.length === 0) {
        const { x, y } = event.target.getStage().getPointerPosition();
        // console.log(x, y)
        const x0 = Math.floor(x / gridSize) * gridSize;
        const y0 = Math.floor(y / gridSize) * gridSize;
        setAnnotation({
          colors: [["#FFFFFFAA", "#FFFFFFAA"], ["#000000AA", "#000000AA"]],
          motif: myAnnotation.motif,
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
    <div>

      <Stage onMouseMove={handleMouseMove} width={numCols * gridSize} height={numRows * gridSize}>
        <Layer>
          <Rect key={"background"}
            x={0}
            y={0}
            width={numCols * gridSize}
            height={numRows * gridSize}
            fill={"#AAAAAA"}
            stroke="transparent"
          />
        </Layer>
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
                fill={myDesign.get_rgba(col, row).hex()}  // Set the fill color based on the state
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
          motif={chosenMotif}
          colors={myAnnotation.colors}
          height={chosenMotif.height()}
          width={chosenMotif.width()}
          gridSize={gridSize}
        />
      </Stage>
      <ButtonPicker color={color}
        setter={setColor}
        />
      <MotifLibrary motif_setter={(motif_name: string, motif: Motif) => (
        () => {
          console.log(`Motif ${motif_name} clicked!`)
          setChosenMotif(motif)
        }
      )}/>
    </div>
  );
};

export default GridCanvas;
