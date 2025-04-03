import React, {useState, useEffect} from "react";
import MotifImage from "./MotifImage";
import './MotifLibrary.css'
import Motif, { Color } from "../core/Motif";
import { group } from "console";
import { getPreEmitDiagnostics } from "typescript";

interface MotifLibraryProps {
    motifs?: string[];
    img_width?: number;
    motif_setter?: (motif_name: string, motif: Motif) => () => void
}

interface Motifable {
    width: number;
    height: number;
    colors: number[][];
}

function isMotifable(obj: any) : obj is Motifable {
    const motifable = (obj as Motifable)
    return obj.width !== undefined && obj.height !== undefined && obj.colors !== undefined
}

function number_to_color(n: number) : Color {
    switch (n) {
        case 1:
            return Color.BACK;
        case 2:
            return Color.FORE;
        case 3:
            return Color.INVIS;
        default:
            throw new Error(`Cannot turn number ${n} into a Color`)

    }
}

const number_lol_to_motif = (numberss: number[][]) => {
    const colors = numberss.map<Color[]>(
        (numbers: number[]) => (
            numbers.map<Color>(
                number_to_color
            )
        )
    )
    return new Motif(colors)
}

const MotifLibrary: React.FC<MotifLibraryProps> = ({
    motifs=["x-3x3", "plus-3x3"],
    img_width=100,
    motif_setter=(motif_name: string, motif: Motif) => (() => console.log(motif_name + " clicked!"))
}) => {
    const [motifsList, setMotifsList] = useState<string[]>(motifs)
    const [motifsDict, setMotifsDict] = useState<Record<string, Motif>>({})
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchMotifNames = async () => {
            try {
                const motif_names_request = new Request("http://127.0.0.1:5000/motifs")
                const motif_names_response = await fetch(motif_names_request)
                // console.log(motif_names_response)
                if (!motif_names_response.ok) {
                    throw new Error(`HTTP error! Status: ${motif_names_response.status}`)
                }
                const motif_names_json = await motif_names_response.json();

                const motifsDictCopy: Record<string, Motif> = {}
                for (const k in motif_names_json.motifs) {
                    if (motif_names_json.motifs.hasOwnProperty(k)) {
                        const obj = motif_names_json.motifs[k];
                        if (isMotifable(obj)) {
                            motifsDictCopy[k] = number_lol_to_motif(obj.colors)
                        }
                    }
                }
                setMotifsDict(motifsDictCopy)

                // console.log(motif_names_json)
                setMotifsList(motif_names_json.data)
            } catch (err) {
                setError("Failed to fetch motif names")
                console.error("Error fetching motif names", err)
            } finally {
                setLoading(false)
            }
        };
        
        fetchMotifNames();
    }, [])

    if (loading) return <p>Loading motif library...</p>
    if (error) return <p style={{color: "red"}}>{error}</p>
    return (
        <div className={"motif-library"}>
            <table>
                <thead>
                <tr>
                    <th>Motif Name</th>
                    <th>Motif Preview</th>
                </tr>
                </thead>
                <tbody>
                {motifsList.map((name, row) => (
                <MotifImage key={row} motif_name={name} img_width={img_width} on_click={motif_setter(name, motifsDict[name])}></MotifImage>
            ))}
                </tbody>
            
            </table>
        </div>
    )
}

export default MotifLibrary