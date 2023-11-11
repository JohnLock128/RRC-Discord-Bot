import discord
from discord.ext import commands
# import asyncio
import re
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import Token
import random
from Google_interact import append_data_to_worksheet as adtw, format_for_upload as ffu
import role_config as rc

intents = discord.Intents.default()
intents.members = True  # This enables member events
intents.message_content = True  # Enable the MESSAGE_CONTENT intent

bot = commands.Bot(command_prefix='!', intents=intents)

sheet_name = Token.Sheet_Name
worksheet_index = Token.Sheet_Index

maxiter = 1000


def new_int(x):
    if x != "":
        x = int(x)
    else:
        x = 1e20
    return x


def nick_gen(data, max_len=32):
    nick = f"{data[1]} {data[2]}"
    var_len = max_len - len(nick)
    majors = ['']
    for i in range(len(data[5])):
        majors.append(f'{majors[i]}{data[5][i]}/')
    for i in range(len(majors)):
        majors[i] = majors[i].rstrip('/')
    end_opts = [
        f"",
        f"'{data[6][2:]}",
        f" '{data[6][2:]}",
        f"-{majors[1]}",
        f" - {majors[1]}",
        f"-{majors[1]}'{data[6][2:]}",
        f"-{majors[1]} '{data[6][2:]}",
        f" - {majors[1]} '{data[6][2:]}"
    ]
    if len(majors) >= 3:
        end_opts += [
            f" - {majors[2]}",
            f"-{majors[2]}",
            f"-{majors[2]}'{data[6][2:]}",
            f"-{majors[2]} '{data[6][2:]}"
        ]
    if len(majors) >= 4:
        end_opts += [
            f" - {majors[3]} '{data[6][2:]}",
            f"-{majors[3]}'{data[6][2:]}",
            f"-{majors[3]} '{data[6][2:]}"
        ]
    if len(majors) >= 5:
        end_opts += [
            f" - {majors[4]} '{data[6][2:]}",
            f"-{majors[4]}'{data[6][2:]}",
            f"-{majors[4]} '{data[6][2:]}"
        ]
    for i in range(len(end_opts)):
        if len(end_opts[-(i+1)]) <= var_len:
            nick += end_opts[-(i+1)]
            break
    return nick


async def set_server_nickname(member, new_nickname):
    try:
        await member.edit(nick=new_nickname)
        return True
    except Exception as e:
        await mod_report(f"An error occurred while setting the nickname: {e}", mention_mod=True)
        return False


async def update_roles(member, role_descriptions):
    try:
        for role_id, has_role in role_descriptions:
            role = member.guild.get_role(int(role_id))

            if role is not None:
                if has_role:
                    await member.add_roles(role)
                else:
                    await member.remove_roles(role)
    except Exception as e:
        await mod_report(f"An error occurred while updating roles: {e}", mention_mod=True)


async def mod_report(message, mention_mod=False):
    user = await bot.fetch_user(Token.Mod_ID)
    channel = await bot.fetch_channel(Token.Channel_ID)
    if mention_mod:
        message = f"{user.mention} {message}"
    await channel.send(message)


@bot.event
async def on_ready():
    await mod_report(f'Logged in as {bot.user.name}')


# @bot.event
# async def on_member_join(member):
#     public_welcome = f'Welcome to the server, {member.mention}!\nTo gain access to the full server we require you complete a brief verification process, to start the process type !verify and I\'ll send you the next steps.'
#
#     welcome_channel = member.guild.system_channel
#     if welcome_channel:
#         await welcome_channel.send(public_welcome)
#     await update_roles(member, rc.case0)


@bot.command()
async def force_verification(ctx, member: discord.Member):
    # Check if the command invoker has permission to use the command
    if ctx.author.guild_permissions.administrator:
        await ctx.send(f'Starting verification process for {member.mention}...')
        await process_verification(member)  # Manually trigger the on_member_join event for the specified member
    else:
        await ctx.send('You do not have permission to use this command.')


@bot.command()
async def verify(ctx):
    await process_verification(ctx.author, reply_channel=ctx.channel)  # Manually trigger the on_member_join event for the sender


async def process_verification(member, reply_channel=None):
    await mod_report("beginning verification for: " + str(member))
    # Send a welcome message in the server channel and DM to the new member
    public_welcome = f'Thank you for beginning the verification process, {member.mention}! I will DM you momentarily to get started.'
    private_welcome = 'In order to verify you for access to the server we ask that you please answer the following 7-8 questions. (be careful not to misspell as there is currently no way to edit responses)'

    if reply_channel:
        await reply_channel.send(public_welcome)

    await member.send(private_welcome)

    # Begin asking questions:
    responses = [member.name]
    response_case = 0

    # Question 1
    iter1 = 0
    while iter1 < maxiter:
        iter1 += 1
        await member.send(
            'What is your preferred(first) name? (please be sure to capitalize appropriately, eg. "John")')
        response = await bot.wait_for('message', check=lambda m: m.author == member)
        if len(response.content) > 15:
            await member.send('Your response is not a valid answer, expected answers must be less than 15 characters')
            continue
        else:
            await member.send(f'Your response: {response.content}')
            responses.append(response.content)
            break

    # Question 2
    iter2 = 0
    while iter2 < maxiter:
        iter2 += 1
        await member.send('What is your family/last name? (please be sure to capitalize appropriately, eg. "Doe")')
        response = await bot.wait_for('message', check=lambda m: m.author == member)
        if len(response.content) > 15:
            await member.send('Your response is not a valid answer, expected answers must be less than 15 characters')
            continue
        else:
            await member.send(f'Your response: {response.content}')
            responses.append(response.content)
            break

    # Question 3
    iter3 = 0
    while iter3 < maxiter:
        iter3 += 1
        await member.send(
            'Please respond with which of the following groups best describes you:``` 1. student\n 2. faculty/staff member\n 3. alumni\n 4. other```(type the number that corresponds to the group)')
        response = await bot.wait_for('message', check=lambda m: m.author == member)
        res = new_int(''.join(filter(str.isdigit, response.content)))
        if 1 <= res <= 4:
            response_case = res
        else:
            await member.send('Your response is not a valid answer, expected answers include: "1", "2", "3",and "4"')
            continue
        await member.send(f'Your response: {["error", "Student", "Faculty/Staff Member", "Alumni", "Other"][int(res)]}')
        responses.append(['error', 'Student', 'Faculty/Staff Member', 'Alumni', 'Other'][int(res)])
        break
    if response_case == 4:
        await member.send(
            'You have indicated that you are in a category other than student, faculty, staff, or alumni, ' +
            'as such I am not currently able to verify you for access to the server. Please message the ' +
            'server moderators and they will be able to further assist you.')

        await mod_report(f"user {member} has attempted guest verification with responses: {responses}", mention_mod=True)

    else:

        # Question 4
        if response_case == 1 or response_case == 2:
            iter4 = 0
            while iter4 < maxiter:
                iter4 += 1
                await member.send('What is your RIN?')
                response = await bot.wait_for('message', check=lambda m: m.author == member)
                res = new_int(''.join(filter(str.isdigit, response.content)))
                if 660000000 < res < 670000000:
                    responses.append(res)
                    await member.send(f'Your response: {res}')
                    break
                else:
                    await member.send(
                        'Your response is not a valid answer, expected answers must be 9 digits starting with 66 (eg. 660000000')
                    continue
        else:
            responses.append('')

        # Question 5
        majors = [
            ['Aeronautical Engineering', 'Aero'],
            ['Applied Physics', 'ApPhys'],
            ['Architecture', 'Archi'],
            ['Biology', 'Bio'],
            ['Biomedical Engineering', 'BME'],
            ['Business Analytics', 'BA'],
            ['Business and Management', 'BMGT'],
            ['Chemical Engineering', 'ChemE'],
            ['Chemistry', 'Chem'],
            ['Civil Engineering', 'CivE'],
            ['Cognitive Science', 'CogSci'],
            ['Computer and Systems Engineering', 'CSE'],
            ['Computer Science', 'CS'],
            ['Economics', 'Econ'],
            ['Electrical Engineering', 'EE'],
            ['Environmental Engineering', 'EnvE'],
            ['Environmental Science', 'EnvS'],
            ['Games and Simulation Arts and Sciences', 'GSAS'],
            ['Geology', 'Geo'],
            ['Industrial and Management Engineering', 'IME'],
            ['Information Technology and Web Science', 'ITWS'],
            ['Materials Engineering', 'MatSci'],
            ['Mathematics', 'Math'],
            ['Mechanical Engineering', 'MechE'],
            ['Music', 'Music'],
            ['Nuclear Engineering', 'NucE'],
            ['Philosophy', 'Phil'],
            ['Physics', 'Phys'],
            ['Psychological Science', 'PsychS'],
            ['Science, Technology, and Society', 'STS'],
            ['Sustainability Studies', 'SustS']
        ]

        iter5 = 0
        while iter5 < maxiter:
            iter5 += 1
            done = 1
            if response_case == 1 or response_case == 3:
                message = ['error', 'Respond with the number(s) that correspond to your current Major(s)', 'error',
                           'Respond with the number(s) that correspond to the degree(s) you received from RPI'][
                              response_case] + ' (if you have a dual and/or double major you may enter multiple numbers separated by commas, eg. "4,27,12" or "9"'
                message += f'``` 0. {majors[0][0]}'
                for i in range(len(majors)-1):
                    message += f'\n {i+1}. {majors[i+1][0]}'
                message += "```"
                await member.send(message)
                response = await bot.wait_for('message', check=lambda m: m.author == member)
                res = ''.join(filter(lambda x: x == ',' or x.isdigit(), response.content))
                res = res.split(',')
                if len(res) < 1:
                    await member.send(
                        f'Your response is not a valid answer, expected answers must include  at least one number between 0 and {len(majors) - 1}')
                    continue
                res_long = []
                res_short = []
                for i in range(len(res)):
                    if new_int(res[i]) >= len(majors) or new_int(res[i]) < 0:
                        await member.send(
                            f'Your response is not a valid answer, expected answers must only include numbers between 0 and {len(majors) - 1}')
                        done = 0
                        break
                    res_long.append(majors[new_int(res[i])][0])
                    res_short.append(majors[new_int(res[i])][1])
                if done == 1:
                    await member.send(f'''Your response: {"".join(filter(lambda x: x != "[" and x != "]" and x != "'", str(res_long)))}''')
                    responses.append(res_short)
                    break
            else:
                await member.send(
                    'What department/group do you work in? (please respond with the abbreviation for your depart or group, eg. ECSE, MANE, CATS etc. this will appear in your server nickname, so please try to keep it short)')
                response = await bot.wait_for('message', check=lambda m: m.author == member)
                if len(response.content) > 10:
                    await member.send(
                        'Your response is not a valid answer, expected answers must be less than 10 characters')
                    continue
                responses.append([response.content])
                await member.send(f'Your response: {response.content}')
                break

        # Question 6
        iter6 = 0
        while iter6 < maxiter:
            iter6 += 1
            if response_case == 2:
                await member.send(
                    'If you graduated from RPI what year did you do so? (please respond with a four-digit year eg. 2000 or "N/A" if you did not graduate from RPI)')
            elif response_case == 3:
                await member.send(
                    'What year did you graduate from RPI? (please respond with a four-digit year eg. 2000)')
            else:
                await member.send(
                    'What is your expected graduation year? (please respond with a four-digit year eg. 2000)')
            response = await bot.wait_for('message', check=lambda m: m.author == member)
            if response_case == 2 and (response.content.count('n') > 0 or response.content.count('N') > 0) and (
                    response.content.count('a') > 0 or response.content.count('A') > 0):
                responses.append(0)
                await member.send(f'Your response: N/A')
                break
            elif len(''.join(filter(str.isdigit, response.content))) == 4:
                res = ''.join(filter(str.isdigit, response.content))
                responses.append(res)
                await member.send(f'Your response: {res}')
                break
            else:
                await member.send(
                    'Your response is not a valid answer, expected answers must be a four-digit number (or N/A for Faculty/Staff)')
                continue

        # Question 7
        iter7 = 0
        while iter7 < maxiter:
            iter7 += 1
            await member.send(
                'Do you agree to follow all rules laid out in the #rules channel of the RPI Robotics Club server? (Please respond with y/n)')
            response = await bot.wait_for('message', check=lambda m: m.author == member)
            if len(''.join(filter(lambda x: x == 'y' or x == 'Y', response.content))):
                await member.send(f'Your response: Yes')
                responses.append('Yes')
                break
            else:
                await member.send(
                    "Agreeing to follow the server rules is a requirement for joining the RPI robotics club discord server, failure to agree to our rules will result in not being permitted access to the rest of the server")
                continue

        # Question 8
        done = 0
        otp_burn = 1
        message = 0
        otp = 0
        iter8 = 0
        while iter8 < maxiter:
            iter8 += 1
            sub_esc = 0
            if response_case != 3:
                await member.send('What is your RPI email address?')
            else:
                await member.send('What is your email address?')
            response = await bot.wait_for('message', check=lambda m: m.author == member)
            if response_case != 3 and response.content[-8:] != "@rpi.edu":
                await member.send(
                    'Your response is not a valid answer, expected answers must be an email address ending with "@rpi.edu"')
                continue
            elif not (re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$', response.content)):
                await member.send('Your response is not a valid answer, expected answers must be a valid email address')
                continue
            else:
                await member.send(f'Your response: {response.content}')
                await member.send(
                    f'you will be sent an email at {response.content} shortly. Please Respond here with the 6-digit code sent in that email, After this  your server verification will be complete!\n(Be sure to check your junk mail as it is likely to be flagged as spam. Additionally, if you need the email to be resent reply "1", and if you need to re-enter your email, reply "2")')
                # Create a SendGrid client
                sg = sendgrid.SendGridAPIClient(api_key=Token.SendGrid)
                iter9 = 0
                while iter9 < maxiter:
                    iter9 += 1
                    if sub_esc == 1:
                        break
                    # Create One-Time-Password
                    if otp_burn == 1:
                        otp = f"{random.randint(0, 999999):06d}"
                        # Create an email
                        from_email = Email("rpiroboticsclub@gmail.com")
                        to_email = To(response.content)
                        subject = "Robotics Club Discord Verification Code"
                        content = Content("text/plain", f"Your Verification Code:\n{otp}")
                        message = Mail(from_email, to_email, subject, content)
                    otp_burn = 1
                    # Send the email
                    reply = sg.client.mail.send.post(request_body=message.get())
                    # Check status
                    if reply.status_code == 202:
                        await member.send("Email sent successfully!")
                        iter10 = 0
                        while iter10 < maxiter:
                            iter10 += 1
                            otp_response = await bot.wait_for('message', check=lambda m: m.author == member)
                            check = new_int(''.join(filter(str.isdigit, otp_response.content)))
                            if check != int(otp) and check != 1 and check != 2:
                                await member.send(
                                    'The code you sent is not valid, please ensure you typed it correctly and try again. (If you need the email to be resent reply "1". If you need to re-enter your email, reply "2")')
                            elif check == 1:
                                break
                            elif check == 2:
                                sub_esc = 1
                                break
                            else:
                                await member.send(
                                    "Your Email is now verified and you will be admitted to the server momentarily")
                                done = 1
                                sub_esc = 1
                                responses.append(response.content)
                                break
                    else:
                        await mod_report(f"Failed to send email. Status code: {reply.status_code}\n{reply.body}",
                                         mention_mod=True)
                        otp_burn = 0
                        continue
            if done == 1:
                break

        # Updates Nickname
        nickname = nick_gen(responses)
        await set_server_nickname(member, nickname)

        if response_case == 1:
            await update_roles(member, rc.case1)
        elif response_case == 2:
            await update_roles(member, rc.case2)
        elif response_case == 3:
            await update_roles(member, rc.case3)

        # notify moderator of new member
        if response_case != 1:
            priority = True
        else:
            priority = False

        mem_type = ['error', "student", "faculty/staff member", "alumnus"][response_case]

        await mod_report(f"new {mem_type} added to server with nickname {nickname}\nresponses: {str(responses)}", mention_mod=priority)

        # Adds data to google sheet
        iter1 = 0
        while iter1 < maxiter:
            iter1 += 1
            try:
                adtw(ffu(responses), sheet_name, worksheet_index)
                break
            except Exception as e:
                await mod_report(f"failed to add data to sheet, error: {e}")


bot.run(Token.Discord)
