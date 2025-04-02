import React, {useState} from 'react';
import { Stage, Layer, Rect } from 'react-konva';
import Motif from './core/Motif';

interface HovererProps {
    colors: string[][];
    motif: Motif;
    x: number;
    y: number;
    height: number;
    width: number;
    gridSize: number;
}

const Hoverer : React.FC<HovererProps> = ({
    colors, motif, x, y, height, width, gridSize
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
                    fill={motif.get_rgba(col, row).filtered(1.0, 1.0, 1.0, 0.5).hex()}
                    stroke="black"
                    strokeWidth={1}
                    />
                ))
        )}
        </Layer>
    );
};

export default Hoverer