import React, {useState, useEffect} from "react";
import MotifImage from "./MotifImage";
import './MotifLibrary.css'

interface MotifLibraryProps {
    motifs?: string[];
    img_width?: number;
}

const MotifLibrary: React.FC<MotifLibraryProps> = ({
    motifs=["x-3x3", "plus-3x3"],
    img_width=100
}) => {
    const [motifsList, setMotifsList] = useState<string[]>(motifs)
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchMotifNames = async () => {
            try {
                const motif_names_request = new Request("http://127.0.0.1:5000/motifs")
                const motif_names_response = await fetch(motif_names_request)
                console.log(motif_names_response)
                if (!motif_names_response.ok) {
                    throw new Error(`HTTP error! Status: ${motif_names_response.status}`)
                }
                const motif_names_json = await motif_names_response.json()
                console.log(motif_names_json)
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
                <MotifImage key={row} motif_name={name} img_width={img_width}></MotifImage>
            ))}
                </tbody>
            
            </table>
        </div>
    )
}

export default MotifLibrary