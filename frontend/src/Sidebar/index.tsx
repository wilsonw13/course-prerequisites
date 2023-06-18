import { useState, Dispatch, SetStateAction, ChangeEvent, FormEvent } from 'react'
import { RxDoubleArrowLeft } from 'react-icons/rx'
import styles from './Sidebar.module.css'
import { Query, QueryValue } from '../interfaces'

interface Props {
  socket: WebSocket | null,
  query: Query,
  setQuery: Dispatch<SetStateAction<Query>>,
}

export default function Sidebar ({ socket, query, setQuery }: Props) {
  const [isOpen, setOpen] = useState<boolean>(true)

  const handleInputChange = (e: ChangeEvent<HTMLFormElement>) => {
    const { name, value, type, checked } = e.target
    let inputValue: QueryValue

    if (type === 'checkbox') {
      inputValue = checked
    } else if (name === 'courses' || name === 'departments') {
      // Parse input values as arrays
      inputValue = value.split(',').map((item: string) => item.toUpperCase().trim())
    } else {
      inputValue = value
    }

    setQuery((prevState: Query) => ({
      ...prevState,
      [name]: inputValue
    }))
  }

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    if (socket) {
      // Send message through the WebSocket connection
      console.log('Sending query', query)

      socket.send(JSON.stringify({ type: 'query', query }))
    }
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
            value={query.courses}
          />
        </div>

        <div>
          <label htmlFor="departments">Departments</label>
          <input
            type="text"
            name="departments"
            value={query.departments}
          />
        </div>

        <div>
          <label htmlFor="show_direct_prerequisites">
            Show Direct Prerequisites
          </label>
          <input
            type="checkbox"
            name="show_direct_prerequisites"
            checked={query.show_direct_prerequisites}
          />
        </div>

        <div>
          <label htmlFor="show_transitive_prerequisites">
            Show Transitive Prerequisites
          </label>
          <input
            type="checkbox"
            name="show_transitive_prerequisites"
            checked={query.show_transitive_prerequisites}
          />
        </div>

        <div>
          <label htmlFor="show_disconnected_courses">
            Show Disconnected Courses
          </label>
          <input
            type="checkbox"
            name="show_disconnected_courses"
            checked={query.show_disconnected_courses}
          />
        </div>
        <button>Query</button>
      </form>
    </div>
  )
}
