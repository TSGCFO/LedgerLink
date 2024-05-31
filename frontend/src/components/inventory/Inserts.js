import React, { useState } from 'react';
import {
    Button,
    TextField,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Checkbox,
    FormControlLabel
} from '@mui/material';

function Inserts() {
    const [inserts, setInserts] = useState([]);
    const [openInsertModal, setOpenInsertModal] = useState(false);
    const [currentInsert, setCurrentInsert] = useState({
        insertName: '',
        description: '',
        sku: [],
        numberOfInserts: '',
        pricePerInsert: '',
        pricingOption: 'fixed'
    });

    const handleInsertChange = (event) => {
        if (event.target.name === 'sku') {
            setCurrentInsert({ ...currentInsert, sku: [...currentInsert.sku, event.target.value] });
        } else {
            setCurrentInsert({ ...currentInsert, [event.target.name]: event.target.value });
        }
    };

    const handleSubmit = () => {
        console.log(currentInsert);
        // Here you would typically handle API call to save insert data
        const newInserts = [...inserts, currentInsert];
        setInserts(newInserts);
        setOpenInsertModal(false);
        setCurrentInsert({ insertName: '', description: '', sku: [], numberOfInserts: '', pricePerInsert: '', pricingOption: 'fixed' }); // Reset form
    };

    const handleDelete = (index) => {
        const newInserts = inserts.filter((_, idx) => idx !== index);
        setInserts(newInserts);
    };

    const handleOpenInsertModal = () => {
        setOpenInsertModal(true);
    };

    const handleCloseInsertModal = () => {
        setOpenInsertModal(false);
    };

    return (
        <div>
            {inserts.map((insert, index) => (
                <div key={index}>
                    <p>{insert.insertName}</p>
                    <Button onClick={() => setCurrentInsert(insert)}>Edit</Button>
                    <Button onClick={() => handleDelete(index)}>Delete</Button>
                </div>
            ))}
            <Button onClick={handleOpenInsertModal}>Create New Insert</Button>
            <Dialog open={openInsertModal} onClose={handleCloseInsertModal}>
                <DialogTitle>Create or Edit Insert</DialogTitle>
                <DialogContent>
                    <TextField fullWidth label="Insert Name" required name="insertName" value={currentInsert.insertName} onChange={handleInsertChange} />
                    <TextField fullWidth label="Description" required name="description" value={currentInsert.description} onChange={handleInsertChange} />
                    <FormControl fullWidth>
                        <InputLabel>SKU</InputLabel>
                        <Select
                            multiple
                            value={currentInsert.sku}
                            onChange={handleInsertChange}
                            name="sku"
                        >
                            {/* Dynamically load SKUs */}
                            <MenuItem value="SKU1">SKU1</MenuItem>
                            <MenuItem value="SKU2">SKU2</MenuItem>
                        </Select>
                    </FormControl>
                    <TextField fullWidth type="number" label="Number of Inserts" required name="numberOfInserts" value={currentInsert.numberOfInserts} onChange={handleInsertChange} />
                    <TextField fullWidth label="Price per Insert" required name="pricePerInsert" value={currentInsert.pricePerInsert} onChange={handleInsertChange} />
                    <FormControlLabel control={<Checkbox checked={currentInsert.pricingOption === 'fixed'} onChange={() => setCurrentInsert({ ...currentInsert, pricingOption: 'fixed' })} />} label="Fixed" />
                    <FormControlLabel control={<Checkbox checked={currentInsert.pricingOption === 'eachSKU'} onChange={() => setCurrentInsert({ ...currentInsert, pricingOption: 'eachSKU' })} />} label="Each SKU" />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseInsertModal}>Cancel</Button>
                    <Button onClick={handleSubmit}>Save and Close</Button>
                </DialogActions>
            </Dialog>
        </div>
    );
}

export default Inserts;
