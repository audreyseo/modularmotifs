import { group } from "console";

export const arrayRange = (start: number, stop: number, step: number) =>
    Array.from(
    { length: (stop - start) / step + 1 },
    (value, index) => start + index * step
    );

export function enumerate<T>(p: Iterable<T, any, any>): Iterable<[number, T], any, any> {
    return Array.from(p).map<[number, T]>((value: T, index: number) => [index, value])
}