import { useState, ChangeEvent } from 'react'
import { RxDoubleArrowLeft } from 'react-icons/rx'
import styles from './Sidebar.module.css'

// interface Props {
// }

export default function Sidebar () {
  const [open, setOpen] = useState<boolean>(true)

  const [query, setQuery] = useState({
    courses: '',
    departments: 'CSE',
    show_direct_prerequisites: false,
    show_transitive_prerequisites: false,
    show_disconnected_courses: true
  })

  const [graphData, setGraphData] = useState(null)

  const handleInputChange = (event: ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = event.target
    let inputValue: string | string[] | boolean

    if (type === 'checkbox') {
      inputValue = checked
    } else if (name === 'courses' || name === 'departments') {
      // Parse input values as arrays
      inputValue = value.split(',').map((item) => item.toUpperCase().trim())
    } else {
      inputValue = value
    }

    setQuery((prevState) => ({
      ...prevState,
      [name]: inputValue
    }))
  }

  const handleSubmit = () => {
    console.log('SUBMIT')
  }

  return (
    <div className={styles.sidebar}>
      <form className={styles.form} onSubmit={handleSubmit}>
        <div>
          <label htmlFor="courses">Courses</label>
          <input
            type="text"
            name="courses"
            value={query.courses}
            onChange={handleInputChange}
          />
        </div>

        <div>
          <label htmlFor="departments">Departments</label>
          <input
            type="text"
            name="departments"
            value={query.departments}
            onChange={handleInputChange}
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
            onChange={handleInputChange}
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
            onChange={handleInputChange}
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
            onChange={handleInputChange}
          />
        </div>
        <button>Query</button>
      </form>
      <RxDoubleArrowLeft className={styles.arrow_icon} />
    </div>
  )
}
