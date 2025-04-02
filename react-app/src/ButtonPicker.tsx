'use strict'

import { group } from 'console';
import React, { useState } from 'react'
import { ChromePicker } from 'react-color'
import RGBAColor from './core/RGBAColor';

interface ColorProp {
    r: number;
    g: number;
    b: number;
    a: number;
  }

interface ButtonProps {
    color: ColorProp;
    setter: React.Dispatch<React.SetStateAction<ColorProp>>
}

interface StateProps {
    displayColorPicker: boolean
}

const ButtonPicker: React.FC<ButtonProps> = ({
    color,
    setter
}) => {
    const [state, setState] = useState<StateProps>({
        displayColorPicker: false
    })

  const handleClick = () => {
    setState({ displayColorPicker: !state.displayColorPicker })
  };

  const handleClose = () => {
    setState({ displayColorPicker: false })
  };

const [mycolor, setMyColor] = useState<ColorProp>(color)
const popover: React.CSSProperties = {
    "position": 'absolute',
    "zIndex": '2',
}
const cover: React.CSSProperties = {
    "position": 'fixed',
    "top": '0px',
    "right": '0px',
    "bottom": '0px',
    "left": '0px',
}

const to_hex = (color: ColorProp) => {
    const rgba = new RGBAColor(color.r, color.g, color.b, color.a)
    return rgba.hex()
}

const changer = (color: any, event: any) => {
    const newcolor = {
        r: color.rgb.r,
        g: color.rgb.g,
        b: color.rgb.b,
        a: (color.rgb.a === undefined) ? 1.0 : color.rgb.a
        }
    setMyColor(newcolor)
    setter(newcolor)
}

const get_background_color = () => {
    return {
        "background": to_hex(mycolor)
    } as React.CSSProperties
}

return (
    <div style={get_background_color()}>
    <button onClick={ handleClick }>Pick Color</button>
    { state.displayColorPicker ? <div style={ popover }>
        <div style={ cover } onClick={ handleClose }/>
        <ChromePicker color={mycolor} onChange={ changer } />
    </div> : null }
    </div>
)
}

export default ButtonPicker