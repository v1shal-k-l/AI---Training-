from os import write

from flask import Flask, request,jsonify
import  json

app = Flask(__name__)

def read_data():
    with open('data.json',"r") as json_file:
        return json.load(json_file)

print(read_data())

@app.route("/students", methods=["GET"])
def get_students():
    students = read_data()
    return jsonify(students)

@app.route("/students/<int:id>", methods=["GET"])
def get_student(id):

    students = read_data()

    for student in students:
        if student["id"] == id:
            return jsonify(student)

    return jsonify({
        "message": "student not found"
    }), 404

def write_data(data):
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)

@app.route("/students", methods=["POST"])
def add_student():
    students = read_data()
    new_student = request.get_json()
    students.append(new_student)


    write_data(students)

    return jsonify({
        "message": "student added successfully"
    })

@app.route("/students/<int:id>", methods=["PUT"])
def update_student(id):
    students = read_data()

    updated_student = request.get_json()

    for student in students:
        if student["id"] == id:

            student["name"] = updated_student["name"]
            student["course"] = updated_student["course"]
            student["score"] = updated_student["score"]

            write_data(students)

            return jsonify(
                {
                    "message": "student updated successfully"
                }
            )

    return jsonify({
        "message": "Student not found"
    }), 404

@app.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):

    students = read_data()

    for student in students:

        if student["id"] == id:

            students.remove(student)

            write_data(students)

            return jsonify({
                "message": "Student deleted successfully"
            })

    return jsonify({
        "message": "Student not found"
    }), 404


if __name__ == "__main__":
    app.run(debug=True)