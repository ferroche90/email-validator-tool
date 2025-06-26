declare module '@mui/material' {
  import type { ComponentType, ReactNode } from 'react'
  
  export const LinearProgress: ComponentType<{ [key: string]: unknown }>
  export const Box: ComponentType<{ children?: ReactNode; [key: string]: unknown }>
  export const Typography: ComponentType<{ children?: ReactNode; [key: string]: unknown }>
  export const Button: ComponentType<{ children?: ReactNode; [key: string]: unknown }>
}

declare module 'papaparse' {
  import Papa from 'papaparse'
  export default Papa
} 