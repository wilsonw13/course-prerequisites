import { useState, Dispatch, SetStateAction, ChangeEvent, FormEvent } from 'react'
import { RxDoubleArrowLeft } from 'react-icons/rx'
import styles from './Sidebar.module.css'
import { QueryForm, QueryFormValue } from '../interfaces'

interface Props {
  socket: WebSocket | null,
  queryForm: QueryForm,
  setQueryForm: Dispatch<SetStateAction<QueryForm>>,
  sendQuery: () => void
}

export interface QueryValid {
  [key: string]: boolean;
}

export default function Sidebar ({ socket, queryForm, setQueryForm, sendQuery }: Props) {
  const [isOpen, setOpen] = useState<boolean>(true)
  const [isQueryValidObj, setQueryValidObj] = useState<QueryValid>({
    courses: true,
    departments: true
  })

  const isQueryValid = () => Object.values(isQueryValidObj).every(Boolean)

  const handleInputChange = (e: ChangeEvent<HTMLFormElement>) => {
    const { name, value, type, checked } = e.target
    let inputValue: QueryFormValue

    if (type === 'checkbox') {
      inputValue = checked
    } else if (name === 'courses' || name === 'departments') {
      // Remove all whitespace and convert to uppercase
      inputValue = value.replace(/\s/g, '').toUpperCase()

      // Validate input values
      let regex: RegExp
      switch (name) {
        case 'courses':
          regex = /^([A-Z]{3}\d{3},?)*$/
          break
        case 'departments':
          regex = /^([A-Z]{3},?)*$/
      }

      setQueryValidObj((prevState) => ({
        ...prevState,
        [name]: regex.test(`${inputValue}`)
      }))
    } else {
      inputValue = value
    }

    setQueryForm((prevState) => ({
      ...prevState,
      [name]: inputValue
    }))
  }

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    sendQuery()
  }

  const containerStyle = `${styles.sidebar} ${isOpen ? '' : styles.sidebar_collapsed}`
  const arrowIronStyle = `${styles.arrow_icon} ${isOpen ? '' : styles.rotate_arrow_icon}`

  return (
    <div className={containerStyle}>
      <RxDoubleArrowLeft className={arrowIronStyle} onClick={() => { setOpen(!isOpen) }} />
      <form className={styles.form} onChange={handleInputChange} onSubmit={handleSubmit}>
        <p>Query Courses</p>
        <div>
          <label htmlFor="courses">Courses</label>
          <input
            type="text"
            name="courses"
            value={queryForm.courses}
          />
        </div>
        {!isQueryValidObj.courses && <p style={{ color: 'red' }}>Please enter valid courses!</p>}
        <div>
          <label htmlFor="departments">Departments</label>
          <input
            type="text"
            name="departments"
            value={queryForm.departments}
          />
        </div>
        {!isQueryValidObj.departments && <p style={{ color: 'red' }}>Please enter valid departments!</p>}
        <div>
          <label htmlFor="show_direct_prerequisites">
            Show Direct Prerequisites
          </label>
          <input
            type="checkbox"
            name="show_direct_prerequisites"
            checked={queryForm.show_direct_prerequisites}
          />
        </div>

        <div>
          <label htmlFor="show_transitive_prerequisites">
            Show Transitive Prerequisites
          </label>
          <input
            type="checkbox"
            name="show_transitive_prerequisites"
            checked={queryForm.show_transitive_prerequisites}
          />
        </div>

        <div>
          <label htmlFor="show_disconnected_courses">
            Show Disconnected Courses
          </label>
          <input
            type="checkbox"
            name="show_disconnected_courses"
            checked={queryForm.show_disconnected_courses}
          />
        </div>
        <button
          className={isQueryValid() ? '' : styles.submitDisabled}
          disabled={!isQueryValid()}>Query</button>
      </form>
    </div>
  )
}
