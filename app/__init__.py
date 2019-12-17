"""
A neural network that reads handwriting from given images.
Based on the project :
'build a handwritten text recognition system'
https://towardsdatascience.com/build-a-handwritten-text-recognition-system-using-tensorflow-2326a3487cd5
"""
import sys
from app.Model import Model
from app.Model import DecoderType
from app.pdf_to_image import convert_pdf_to_image
from app.line_segmentation import line_segmentation, crop_and_warp
from app.word_segmentation import word_segmentation, prepare_image, find_rect, show_image, save_word_image, get_words_image
import os
import cv2
import argparse
from view.models import Answersheet
from view.models import Team
from view.models import SubAnswerGiven
from view.models import SubAnswer
from view.models import Question
from view.models import Variant
from view.config import InputConfig
import numpy as np


def process_sheet(answer_sheet_image, model, save_image=False, sheet_name="scan", db=None, answersheet_id=None):
    word_index = 0
    # gray = cv2.cvtColor(answer_sheet_image, cv2.COLOR_BGR2GRAY)
    # Now we have the answer sheet in image form and we can move on to the line segmentation
    output_folder = "out/"
    lines = line_segmentation(answer_sheet_image, save_image, output_folder, sheet_name, db, answersheet_id)

    # We keep track of which question is being handled, because 1 question can have multiple lines
    previous_question = -1
    subanswer_number = 0
    # After the line segmentation is done we can find the separate words
    for line_image in lines:
        print("processing line: " + str(line_image[2]))
        line = line_image[0]
        # -kernelSize: size of filter kernel (odd integer)
        # -sigma: standard deviation of Gaussian function used for filter kernel
        # -theta: approximated width/height ratio of words, filter function is distorted by this factor
        # - min_area: ignore word candidates smaller than specified area
        original_height = line.shape[0]
        resized_height = 50
        multiply_factor = original_height / resized_height
        # After the resizing, the size of the number box will always be around this value.
        number_box_size = 66
        line = prepare_image(line, resized_height, number_box_size)
        # TODO test out the theta and min_area parameter changes if the results are not good.
        res = word_segmentation(line, kernel_size=25, sigma=11, theta=7, min_area=100)

        # iterate over all segmented words
        # print('Segmented into %d words' % len(res))
        # if save_image:
        #     save_word_image(output_folder, sheet_name, line_image, multiply_factor, res, db, number_box_size)
        # #
        # We can now examine each word.
        words = get_words_image(line_image, multiply_factor, res, number_box_size, db, model, answersheet_id)
        # words_results = []
        # predicted_line = ""
        # for word in words:
        #     print("reading words")
        #     # # TODO add contrast to each word
        #     read_results = read_word_from_image(word[0], model)
        #     word_index += 1
        #     words_results.append(read_results)
        #     # print(words_results)
        #     predicted_line = predicted_line + str(read_results[0]) + " "
        #     # TODO @Sander: save prediciton with the word

        # We now want to save the details of this line with the answer given
        # if db is not None:
        #     answersheet_detail = InputConfig.page_lines[1]
        #     print("answersheet number " + str(answersheet_id))
        #     line_detail = answersheet_detail[line_image[2]]
        #     print("line detail " + str(line_detail))
        #     if str(line_detail).isdigit():
        #         print("This line is a valid question")
        #         # If it's a digit we know it is a correct question, so we can start finding the question details
        #         # TODO @Sander: find correct question id (possibly configuration)
        #         # We assume the configuration is always correct. It returns a question id and a subanswer id
        #         question_id = InputConfig.question_to_id.get(str(line_detail))
        #         if question_id == previous_question:
        #             subanswer_number += 1
        #         else:
        #             previous_question = question_id
        #             subanswer_number = 0
        #         sub_answer_id = question_id[1][subanswer_number]
        #         print("question id " + str(question_id))
        #         question = Question.query.filter_by(id=question_id[0]).first()
        #         sub_answer = SubAnswer.query.filter_by(id=sub_answer_id).first()
        #         # TODO @Sander: For now we assume there is only 1. Solve this later.
        #         variant = Variant.query.filter_by(subanswer_id=sub_answer.id).first()
        #
        #         print("sub_answer id " + str(sub_answer.id))
        #         print("variant id " + str(variant.id))
        #         # get the team. The answersheet_id should always exist in the database and should always be exactly one
        #         answersheet = Answersheet.query.filter_by(id=answersheet_id).first()
        #         team_id = answersheet.get_team_id()
        #         team = Team.query.filter_by(id=team_id).first()
        #         answered_by = team.get_team_name()
        #         print("team_id  " + str(team_id))
        #         print("answered_by " + str(answered_by))
        #         # correct is always false at first and can be set to True later
        #         # TODO @Sander: person_id is now always the same, how will this be determined?
        #         #     checkedby="answerchecker",
        #         # corr_answer = variant.get_answer(),
        #         #     answered_by=answered_by,
        #         #     confidence=words_results[1],
        #         sub_answer_given = SubAnswerGiven(
        #             question_id=question_id[0],
        #             team_id=team_id,
        #             corr_answer_id=sub_answer.id,
        #             person_id=2,
        #             correct=False,
        #             line_id=line_image[2],
        #             answer_given=predicted_line
        #         )
        #         db.session.add(sub_answer_given)
        #         db.session.commit()



def run_program(pubquiz_answer_sheets, save_image=False, db=None):
    print("De officiele Ordina pub-quiz antwoord vinder")
    model = Model(open('model/charList.txt').read())

    for answer_sheets in pubquiz_answer_sheets:
        # The pdf file. We can it and it returns 1 to multiple answer pages
        pages = convert_pdf_to_image(answer_sheets)
        for p in range(0, len(pages)):
            # We take the name from the file. But we want it without any extension.
            file_extension = os.path.splitext(answer_sheets)
            sheet_name = answer_sheets
            if file_extension[1] == ".pdf":
                sheet_name = sheet_name[0:-4]
            sheet_name = sheet_name + "_" + str(p)

            answersheet_id = 0
            if db is not None:
                print("linking team to page")
                # We will link the answersheet to the correct team. If it does not exist we will create it.
                team = Team.query.filter_by(teamname=InputConfig.team_page[p]).first()
                if team is None:
                    # The team does not exist yet, so we will create it with 0 score.
                    new_team = Team(
                        teamname=InputConfig.team_page[p],
                        score=0
                    )
                    db.session.add(new_team)
                    # We already commit it because we need to query it right after to find the id.
                    db.session.commit()

                print("saving answersheet to the database")
                # Save the image to the database!
                # convert the image to byte array so it can be saved in the database
                answer = pages[p].tostring()
                # create an Image object to store it in the database
                width = len(pages[p])
                height = len(pages[p][0])

                # We know a team exists with the configured name because if it didn't we just created it.
                team = Team.query.filter_by(teamname=InputConfig.team_page[p]).first()
                new_answersheet = Answersheet(
                    answersheet_image=answer,
                    team_id=team.id,
                    image_width=width,
                    image_height=height
                )
                # add the object to the database session
                db.session.add(new_answersheet)
                # commit the session so that the image is stored in the database
                db.session.commit()
                answersheet_id = new_answersheet.id

            process_sheet(pages[p], model, save_image, sheet_name, db, answersheet_id)


def save_answersheet():
    pubquiz_anser_sheets = 'scan.pdf'
    pages = convert_pdf_to_image(pubquiz_anser_sheets)
    return pages

