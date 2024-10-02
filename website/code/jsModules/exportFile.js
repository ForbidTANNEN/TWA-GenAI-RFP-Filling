//Handles the export button of the final QA pairs

import { session } from './sessionManager.js';

//Downloads given data as an excel file
function downloadExcel(data, filename = 'data.xlsx') {

    const worksheet = XLSX.utils.json_to_sheet(data);

    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1');

    const wbout = XLSX.write(workbook, {bookType:'xlsx', type:'binary'});

    function s2ab(s) { 
        const buf = new ArrayBuffer(s.length);
        const view = new Uint8Array(buf);
        for (let i=0; i<s.length; i++) view[i] = s.charCodeAt(i) & 0xFF;
        return buf;
    }

    const blob = new Blob([s2ab(wbout)], {type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});

    let link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;

    document.body.appendChild(link);
    link.click(); 

    document.body.removeChild(link);
}

//Clean up QA list and then download file
export function exportFile(){

    const cleanedQAList = session.qaList.map(item => {
        return {
            Questions: item.question,
            Answers: item.answer
        };
    });

    downloadExcel(cleanedQAList)

}