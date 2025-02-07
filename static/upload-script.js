document.addEventListener('DOMContentLoaded', () => {
  const dragArea = document.querySelector('.file-container');
  const dragText = document.querySelector('.header'); 

 
  if (dragArea) {
    console.log('Drag area found');

    dragArea.addEventListener('dragover', (event) => {
      event.preventDefault();  // Allow the drop
      dragText.textContent = 'drop the file here';
      dragArea.classList.add('active'); 
      console.log('File is inside the drag area');
    });

    dragArea.addEventListener('dragleave', () => {
      console.log('File left the drag area');
      dragText.textContent = 'drag or select a file'
      dragArea.classList.remove('active'); 
    });

    dragArea.addEventListener('drop', (event) => {
      event.preventDefault();
      file = event.dataTransfer.files[0]; 
      console.log(file); 
    });
  } else {
    console.log('Drag area element not found');
  }

  
});

 