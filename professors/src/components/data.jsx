import { 
  ListTodo, 
  CheckCircle2, 
  PauseCircle, 
  XCircle, 
  Trash2 
} from "lucide-react";

export const STATUS_OPTIONS = ["Ongoing", "Completed", "On Hold", "Dropped", "Terminated"];

export const SAMPLE_WORKLETS = [
    {
      id: 1,
      title: '25TST04WT',
      status: 'Ongoing',
      progress: 60,
      description: 'AI-driven sentiment analysis for customer.',
      imageUrl: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=400&auto=format&fit=crop',
      startDate: 'Aug 1, 2025',
      endDate: 'Dec 15, 2025',
      students: ['Alice Johnson', 'Bob Williams', 'Charlie Brown'],
    },
    {
      id: 2,
      title: '25TST05SRM',
      status: 'Ongoing',
      progress: 70,
      description: 'Cross-platform mobile app for internal comms.',
      imageUrl: 'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?q=80&w=400&auto=format&fit=crop',
      startDate: 'Sep 1, 2025',
      endDate: 'Jan 30, 2026',
      students: ['Diana Prince', 'Clark Kent'],
    },
    {
      id: 3,
      title: '24ARC01RV',
      status: 'Ongoing',
      progress: 95,
      description: 'Cloud infrastructure migration to AWS with CI/CD.',
      imageUrl: 'https://images.unsplash.com/photo-1587620962725-abab7fe55159?q=80&w=400&auto=format&fit=crop',
      startDate: 'Jul 15, 2025',
      endDate: 'Oct 20, 2025',
      students: [
        'Bruce Wayne',
        'Peter Parker',
        'Tony Stark',
        'Steve Rogers',
        
        
        
      ], // Added more students to test scroll
    },
    {
      id: 4,
      title: '25DES02XI',
      status: 'Ongoing',
      progress: 25,
      description: 'UI/UX redesign for the main customer portal.',
      imageUrl: 'https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?q=80&w=400&auto=format&fit=crop',
      startDate: 'Aug 20, 2025',
      endDate: 'Nov 10, 2025',
      students: ['Carol Danvers', 'Hope van Dyne'],
    },
    {
      id: 5,
      title: '25SEC03LP',
      status: 'Ongoing',
      progress: 40,
      description: 'End-to-end encryption for messaging service.',
      imageUrl: 'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?q=80&w=400&auto=format&fit=crop',
      startDate: 'Sep 10, 2025',
      endDate: 'Feb 1, 2026',
      students: ['Vision', 'Scott Lang', 'Sam Wilson'],
    },
    {
      id: 6,
      title: '25DAT06MU',
      status: 'Ongoing',
      progress: 85,
      description: 'Data warehousing solution for sales analytics.',
      imageUrl: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=400&auto=format&fit=crop',
      startDate: 'Jun 5, 2025',
      endDate: 'Sep 30, 2025',
      students: ['Loki Laufeyson', 'Bucky Barnes'],
    },
];

export const statusIcons = {
  Ongoing: <ListTodo size={24} />,
  Completed: <CheckCircle2 size={24} />,
  "On Hold": <PauseCircle size={24} />,
  Dropped: <XCircle size={24} />,
  Terminated: <Trash2 size={24} />,
};