const express = require('express');
const path = require('path');
const { spawn } = require('child_process');
const bodyParser = require('body-parser');
const msgpack = require('msgpack-lite');

const app = express();
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'views', 'index.html'));
});

app.post('/calculate', (req, res) => {
    const inputData = JSON.stringify(req.body);

    const pythonProcess = spawn('python', ['calculate.py', inputData]);

    let dataChunks = [];
    
    pythonProcess.stdout.on('data', (data) => {
        dataChunks.push(data);
    });

    pythonProcess.stdout.on('end', () => {
        try {
            const buffer = Buffer.concat(dataChunks);
            const decodedData = msgpack.decode(buffer);

            // Assume the decodedData is an array where:
            // - decodedData[0] is the result array (numpy array)
            // - decodedData[1] is the DataFrame (serialized)

            const resultArray = decodedData[0];  // Your 2D array
            const resultDF = decodedData[1];     // Serialized DataFrame (if needed)

            // Send the array to the frontend for plotting
            res.json({ array: resultArray, dataframe: resultDF });
        } catch (error) {
            console.error('Error decoding MessagePack:', error);
            res.status(500).send({ error: 'Error decoding MessagePack' });
        }
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            res.status(500).send({ error: 'An error occurred while executing the Python script' });
        }
    });
});

app.listen(3000, () => {
    console.log('Server running at http://localhost:3000');
});
