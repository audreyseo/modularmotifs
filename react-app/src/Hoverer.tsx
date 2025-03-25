import React, {useState} from 'react';
import { Stage, Layer, Rect } from 'react-konva';

interface HovererProps {
    colors: string[][];
    x: number;
    y: number;
    height: number;
    width: number;
    gridSize: number;
}

const Hoverer : React.FC<HovererProps> = ({
    colors, x, y, height, width, gridSize
}) => {
    return (
        <Layer listening={false}>
            {Array.from({ length: height }).map((_: unknown, row: number) =>
                Array.from({ length: width }).map((_, col) => (
                    <Rect
                    key={`${row}-${col}`}
                    x={x + col * gridSize}
                    y={y + row * gridSize}
                    width={gridSize}
                    height={gridSize}
                    fill={colors[row][col]}
                    stroke="black"
                    strokeWidth={1}
                    />
                ))
        )}
        </Layer>
    );
};

export default Hoverer