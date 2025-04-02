import RGBAColor from './RGBAColor'

abstract class PixelGrid {
    abstract width(): number
    abstract height(): number
    abstract get_rgba(x: number, y: number): RGBAColor

    in_range(x: number, y: number) : boolean {
        return 0 <= x && x < this.width() && 0 <= y && y < this.height()
    }
}

export default PixelGrid