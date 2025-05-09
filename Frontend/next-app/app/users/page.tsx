// 'use client';

// import React, { useState } from 'react';

// interface Course {
//   name: string;
//   number: string;
// }

// const UsersPage = () => {
//   const [courses, setCourses] = useState<Course[]>([{ name: '', number: '' }]);
//   const [schedules, setSchedules] = useState<any[]>([]);

//   const handleChange = (index: number, field: keyof Course, value: string) => {
//     const updatedCourses = [...courses];
//     updatedCourses[index][field] = value;
//     setCourses(updatedCourses);
//   };

//   const addCourse = () => {
//     setCourses([...courses, { name: '', number: '' }]);
//   };

//   const removeCourse = (index: number) => {
//     const updatedCourses = courses.filter((_, i) => i !== index);
//     setCourses(updatedCourses);
//   };

//   const handleSubmit = async (e: React.FormEvent) => {
//     e.preventDefault();

//     const formattedCourses = courses
//       .filter(course => course.name && course.number)
//       .map(course => `${course.name.trim().toUpperCase()} ${course.number.trim()}`);

//     try {
//       const response = await fetch('http://localhost:8000/generate', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ courses: formattedCourses }),
//       });

//       const data = await response.json();
//       console.log('Response from API:', data.schedules);
//       console.log(typeof(data.schedules))
//       setSchedules(data.schedules);
//     } catch (error) {
//       console.error('Error while fetching:', error);
//     }
//   };

//   return (
//     <div className="min-h-screen bg-gray-50 text-gray-800 p-6 font-sans">
//       {/* Header */}
//       <header className="mb-10 text-center">
//         <h1 className="text-5xl text-yellow-400 font-extrabold">WATsched</h1>
//         <p className="text-lg mt-2 text-gray-600">Get all possible schedules for your semester</p>
//       </header>

//       {/* Form */}
//       <form onSubmit={handleSubmit} className="max-w-xl mx-auto bg-white shadow-md rounded-lg p-6 space-y-4">
//         {courses.map((course, index) => (
//           <div key={index} className="flex items-center gap-3">
//             <input
//               type="text"
//               placeholder="Course Name"
//               value={course.name}
//               onChange={(e) => handleChange(index, 'name', e.target.value)}
//               className="flex-1 border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring focus:ring-blue-300"
//             />
//             <input
//               type="text"
//               placeholder="Course Number"
//               value={course.number}
//               onChange={(e) => handleChange(index, 'number', e.target.value)}
//               className="flex-1 border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring focus:ring-blue-300"
//             />
//             {index === courses.length - 1 && (
//               <button
//                 type="button"
//                 onClick={addCourse}
//                 className="text-white bg-green-500 px-3 py-1 rounded hover:bg-green-600"
//               >
//                 +
//               </button>
//             )}
//             {courses.length > 1 && (
//               <button
//                 type="button"
//                 onClick={() => removeCourse(index)}
//                 className="text-white bg-red-500 px-3 py-1 rounded hover:bg-red-600"
//               >
//                 -
//               </button>
//             )}
//           </div>
//         ))}

//         <button
//           type="submit"
//           className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded"
//         >
//           Generate Schedules
//         </button>
//       </form>

//       {/* API Result */}
//       <div className="p-4">
//       <h1 className="text-3xl font-bold text-gold-600 mb-4">Generated Schedules</h1>
//       {schedules.length === 0 ? (
//         <p className="text-gray-500">Loading schedules...</p>
//       ) : (
//         schedules.map((schedule, index) => (
//           <div key={index} className="mb-6 border border-gray-300 rounded-xl p-4 shadow-md bg-white">
//             <h2 className="text-xl font-semibold mb-2">Schedule {index + 1}</h2>
//             <ul className="space-y-2">
//               {schedule.map((cls, idx) => (
//                 <li key={idx} className="p-2 border rounded-md bg-gray-100">
//                   <p><strong>Course:</strong> {cls.course}</p>
//                   <p><strong>Section:</strong> {cls.section}</p>
//                   <p><strong>Time:</strong> {cls.start} - {cls.end}</p>
//                   <p><strong>Days:</strong> {cls.days.join(', ')}</p>
//                 </li>
//               ))}
//             </ul>
//           </div>
//         ))
//       )}
//     </div>


//     </div>


//   );
// };

// export default UsersPage;

'use client';

import React, { useState } from 'react';

interface Course {
name: string;
number: string;
}

interface ClassSection {
course: string;
section: string;
start: string;
end: string;
days: string[];
// Add any other properties your API might return
}

const UsersPage = () => {
const [courses, setCourses] = useState<Course[]>([{ name: '', number: '' }]);
const [schedules, setSchedules] = useState<ClassSection[][]>([]);
const [isLoading, setIsLoading] = useState<boolean>(false);
const [error, setError] = useState<string | null>(null);

const handleChange = (index: number, field: keyof Course, value: string) => {
const updatedCourses = [...courses];
updatedCourses[index][field] = value;
setCourses(updatedCourses);
};

const addCourse = () => {
setCourses([...courses, { name: '', number: '' }]);
};

const removeCourse = (index: number) => {
const updatedCourses = courses.filter((_, i) => i !== index);
setCourses(updatedCourses);
};

const handleSubmit = async (e: React.FormEvent) => {
e.preventDefault();
setIsLoading(true);
setError(null);
setSchedules([]);

const formattedCourses = courses
.filter(course => course.name && course.number)
.map(course => `${course.name.trim().toUpperCase()} ${course.number.trim()}`);

try {
const response = await fetch('http://localhost:8000/generate', {
method: 'POST',
headers: {
  'Content-Type': 'application/json',
},
body: JSON.stringify({ courses: formattedCourses }),
});

if (!response.ok) {
throw new Error(`Server returned ${response.status}: ${response.statusText}`);
}

const data = await response.json();
console.log('Response from API:', data);

// Debug the response structure
console.log('Response type:', typeof data);

// Check for schedules property in the response
if (data && data.schedules) {
// If schedules is a string (from the LLM response), try to parse it
if (typeof data.schedules === 'string') {
  console.log('Received string response in schedules property');
  try {
    // Remove any leading/trailing whitespace that might cause JSON parse errors
    const cleanedString = data.schedules.trim();
    const parsedSchedules = JSON.parse(cleanedString);
    console.log('Parsed schedules data:', parsedSchedules);
    
    if (Array.isArray(parsedSchedules)) {
      setSchedules(parsedSchedules);
    } else {
      setError('Invalid schedules format - expected an array');
      console.error('Invalid parsed schedules format:', parsedSchedules);
    }
  } catch (parseError) {
    console.error('Error parsing schedules string:', parseError);
    setError('Error parsing schedule data');
  }
} else if (Array.isArray(data.schedules)) {
  // If it's already an array
  setSchedules(data.schedules);
} else {
  setError('Unexpected schedules format');
  console.error('Unexpected schedules format:', data.schedules);
}
} else if (data && Array.isArray(data)) {
// If the response is already an array
setSchedules(data);
} else if (data && Array.isArray(data.all_schedules)) {
setSchedules(data.all_schedules);
} else {
setError('Could not find schedules in the response');
console.error('Missing schedules in response:', data);
}
} catch (error) {
console.error('Error while fetching:', error);
setError('Failed to generate schedules. Please try again.');
} finally {
setIsLoading(false);
}
};

return (
<div className="min-h-screen bg-gray-50 text-gray-800 p-6 font-sans">
{/* Header */}
<header className="mb-10 text-center">
<h1 className="text-5xl text-yellow-400 font-extrabold">WATsched</h1>
<p className="text-lg mt-2 text-gray-600">Get all possible schedules for your semester</p>
</header>

{/* Form */}
<form onSubmit={handleSubmit} className="max-w-xl mx-auto bg-white shadow-md rounded-lg p-6 space-y-4">
{courses.map((course, index) => (
  <div key={index} className="flex items-center gap-3">
    <input
      type="text"
      placeholder="Course Name"
      value={course.name}
      onChange={(e) => handleChange(index, 'name', e.target.value)}
      className="flex-1 border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring focus:ring-blue-300"
    />
    <input
      type="text"
      placeholder="Course Number"
      value={course.number}
      onChange={(e) => handleChange(index, 'number', e.target.value)}
      className="flex-1 border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring focus:ring-blue-300"
    />
    {index === courses.length - 1 && (
      <button
        type="button"
        onClick={addCourse}
        className="text-white bg-green-500 px-3 py-1 rounded hover:bg-green-600"
      >
        +
      </button>
    )}
    {courses.length > 1 && (
      <button
        type="button"
        onClick={() => removeCourse(index)}
        className="text-white bg-red-500 px-3 py-1 rounded hover:bg-red-600"
      >
        -
      </button>
    )}
  </div>
))}

<button
  type="submit"
  disabled={isLoading}
  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded disabled:bg-blue-400"
>
  {isLoading ? 'Generating...' : 'Generate Schedules'}
</button>
</form>

{/* API Result */}
<div className="mt-8 max-w-4xl mx-auto">
<h2 className="text-2xl font-bold text-gray-800 mb-4">Generated Schedules</h2>

{error && (
  <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded mb-4">
    {error}
  </div>
)}

{isLoading && (
  <div className="text-center p-8">
    <p className="text-gray-600">Generating schedules...</p>
  </div>
)}

{!isLoading && !error && (!schedules || schedules.length === 0) && (
  <div className="text-center p-8 bg-gray-100 rounded-lg">
    <p className="text-gray-600">No schedules to display. Please submit the form to generate schedules.</p>
  </div>
)}

{!isLoading && schedules && schedules.length > 0 && (
  <div className="grid gap-6 md:grid-cols-2">
    {schedules.map((schedule, index) => (
      <div key={index} className="border border-gray-300 rounded-xl p-4 shadow-md bg-white">
        <h3 className="text-xl font-semibold mb-3 text-blue-600">Schedule {index + 1}</h3>
        <div className="space-y-3">
          {schedule.map((cls, idx) => (
            <div key={idx} className="p-3 border rounded-md bg-gray-50">
              <p className="font-medium">{cls.course}</p>
              <p><span className="text-gray-600">Section:</span> {cls.section}</p>
              <p><span className="text-gray-600">Time:</span> {cls.start} - {cls.end}</p>
              <p><span className="text-gray-600">Days:</span> {cls.days.join(', ')}</p>
            </div>
          ))}
        </div>
      </div>
    ))}
  </div>
)}
</div>
</div>
);
};

export default UsersPage;