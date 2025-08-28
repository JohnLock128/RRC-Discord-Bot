import discord
from discord.ext import commands
import re
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from Configs import role_config as rc
import random
import Data_interact as Di
from config import CONFIG


intents = discord.Intents.default()
intents.members = True  # This enables member events
intents.message_content = True  # Enable the MESSAGE_CONTENT intent

bot = commands.Bot(command_prefix='!', intents=intents)

sheet_name = CONFIG.sheet_name
worksheet_index = CONFIG.sheet_index

maxiter = 1000

majors = [['Aeronautical Engineering', 'Aero'],
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
          ['Sustainability Studies', 'SustS']]


def new_int(x):
    if x != "":
        x = int(x)
    else:
        x = 1e20
    return x


def nick_gen(data, max_len=32):
    nick = f"{data[1]} {data[2]}"
    var_len = max_len - len(nick)
    if data[3][1] != "F":
        major = ['']
        major_data = data[5].split("/")
        for i in range(len(major_data)):
            major.append(f'{major[i]}{major_data[i]}/')
        for i in range(len(major)):
            major[i] = major[i].rstrip('/')
        end_opts = [
            f"",
            f"'{data[6][2:]}",
            f" '{data[6][2:]}",
            f"-{major[1]}",
            f" - {major[1]}",
            f"-{major[1]}'{data[6][2:]}",
            f"-{major[1]} '{data[6][2:]}",
            f" - {major[1]} '{data[6][2:]}"
        ]
        if len(major) >= 3:
            end_opts += [
                f" - {major[2]}",
                f"-{major[2]}",
                f"-{major[2]}'{data[6][2:]}",
                f"-{major[2]} '{data[6][2:]}"
            ]
        if len(major) >= 4:
            end_opts += [
                f" - {major[3]} '{data[6][2:]}",
                f"-{major[3]}'{data[6][2:]}",
                f"-{major[3]} '{data[6][2:]}"
            ]
        if len(major) >= 5:
            end_opts += [
                f" - {major[4]} '{data[6][2:]}",
                f"-{major[4]}'{data[6][2:]}",
                f"-{major[4]} '{data[6][2:]}"
            ]
    elif data[6] == "":
        end_opts = [
            f"",
            f"-{data[5]}",
            f" - {data[5]}",
        ]
    else:
        end_opts = [
            f"",
            f"'{data[6][2:]}",
            f" '{data[6][2:]}",
            f"-{data[5]}",
            f" - {data[5]}",
            f"-{data[5]}'{data[6][2:]}",
            f"-{data[5]} '{data[6][2:]}",
            f" - {data[5]} '{data[6][2:]}"
        ]

    for i in range(len(end_opts)):
        if len(end_opts[-(i + 1)]) <= var_len:
            nick += end_opts[-(i + 1)]
            break
    return nick


async def set_server_nickname(member, new_nickname):
    try:
        await member.edit(nick=new_nickname)
        return True
    except Exception as e:
        await mod_report(f"An error occurred while setting the nickname: {e}", mention_mod=True)
        return False


async def nick_set(member):
    old_nick = member.display_name
    new_nick = nick_gen(Di.get_data(member.id))
    await set_server_nickname(member, new_nick)
    await mod_report(f'updated nickname for user {member.id} from "{old_nick}" to "{new_nick}"')


async def update_roles(member, role_descriptions, keep_only_specified=False):
    try:
        # Convert the role_descriptions to a set for faster lookup
        specified_roles = {int(role_id) for role_id, has_role in role_descriptions if has_role}

        # Remove all roles other than the specified ones if requested
        if keep_only_specified:
            roles_to_remove = [role for role in member.roles if role.id not in specified_roles]
            await member.remove_roles(*roles_to_remove)

        # Add or remove roles based on the role_descriptions
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
    channel = await bot.fetch_channel(CONFIG.modmail_channel_id)
    if mention_mod:
        # FIXME `fetch_user` expects a user ID but the config defines a role ID
        user = await bot.fetch_user(CONFIG.modmail_role_id)
        message = f"{user.mention} {message}"
    await channel.send(message)


async def ask_fname(member):
    it = 0
    while it < maxiter:
        it += 1
        await member.send(
            'What is your preferred(first) name? (please be sure to capitalize appropriately, eg. "John")')
        response = await bot.wait_for('message', check=lambda m: m.author == member and isinstance(m.channel, discord.DMChannel))
        if len(response.content) > 15:
            await member.send('Your response is not a valid answer, expected answers must be less than 15 characters')
            continue
        else:
            await member.send(f'Your response: {response.content}')
            return response.content


async def ask_lname(member):
    it = 0
    while it < maxiter:
        it += 1
        await member.send('What is your family/last name? (please be sure to capitalize appropriately, eg. "Doe")')
        response = await bot.wait_for('message', check=lambda m: m.author == member and isinstance(m.channel, discord.DMChannel))
        if len(response.content) > 15:
            await member.send('Your response is not a valid answer, expected answers must be less than 15 characters')
            continue
        else:
            await member.send(f'Your response: {response.content}')
            return response.content


async def ask_type(member, allow_guest=True):
    it = 0
    while it < maxiter:
        it += 1
        await member.send(
            'Please respond with which of the following groups best describes you:``` 1. student\n 2. faculty/staff member\n 3. alumni\n 4. other```(type the number that corresponds to the group)')
        response = await bot.wait_for('message', check=lambda m: m.author == member and isinstance(m.channel, discord.DMChannel))
        res = new_int(''.join(filter(str.isdigit, response.content)))
        if 1 <= res <= 4:
            case = int(res)
        else:
            await member.send('Your response is not a valid answer, expected answers include: "1", "2", "3",and "4"')
            continue
        await member.send(f'Your response: {["error", "Student", "Faculty/Staff Member", "Alumni", "Other"][case]}')
        if case == 4 and allow_guest:
            await member.send(
                'You have indicated that you are in a category other than student, faculty, staff, or alumni, ' +
                'as such I am not currently able to verify you for access to the server. Please message the ' +
                'server moderators and they will be able to further assist you.')

            await mod_report(f"user {member} has attempted guest verification.", mention_mod=True)
            return ['error', 'Student', 'Faculty/Staff Member', 'Alumni', 'Other'][case], False
        elif case == 4:
            await member.send('Your response is not a valid answer, this bot does not currently support guest admission, if you need further assistance please reach out to the server moderators and they can better assist you.')
            continue
        else:
            return ['error', 'Student', 'Faculty/Staff Member', 'Alumni', 'Other'][case], case


async def ask_rin(member, response_case, updating_row=None):
    if response_case == 1 or response_case == 2:
        it = 0
        while it < maxiter:
            it += 1
            await member.send('What is your RIN?')
            response = await bot.wait_for('message', check=lambda m: m.author == member and isinstance(m.channel, discord.DMChannel))
            res = new_int(''.join(filter(str.isdigit, response.content)))
            if 660000000 < res < 670000000 and Di.unique_on_col(res, 4, ignore_row_index=updating_row):
                await member.send(f'Your response: {res}')
                return res
            else:
                if Di.unique_on_col(res, 4, ignore_row_index=updating_row):
                    await member.send(
                        'Your response is not a valid answer, expected answers must be 9 digits starting with 66 (eg. 660000000)')
                    continue
                else:
                    await member.send(
                        'Your response is not a valid answer, this is a duplicate value with another member\'s data and is therefore not allowed in order to prevent alt accounts.(if you believe this is an error, or you would like to request permission for an alt account, please contact our moderators an they can assist you)')
                    continue
    else:
        return ""


async def ask_major(member, response_case):
    it = 0
    while it < maxiter:
        it += 1
        done = 1
        if response_case == 1 or response_case == 3:
            message = ['error', 'Respond with the number(s) that correspond to your current Major(s)', 'error',
                       'Respond with the number(s) that correspond to the degree(s) you received from RPI'][
                          response_case] + ' (if you have a dual and/or double major you may enter multiple numbers separated by commas, eg. "4,27,12" or "9"'
            message += f'``` 0. {majors[0][0]}'
            for i in range(len(majors) - 1):
                message += f'\n {i + 1}. {majors[i + 1][0]}'
            message += "```"
            await member.send(message)
            response = await bot.wait_for('message', check=lambda m: m.author == member and isinstance(m.channel, discord.DMChannel))
            res = ''.join(filter(lambda x: x == ',' or x.isdigit(), response.content))
            res = res.split(',')
            if len(res) < 1:
                await member.send(
                    f'Your response is not a valid answer, expected answers must include  at least one number between 0 and {len(majors) - 1}')
                continue
            res_long = []
            res_short = ""
            for i in range(len(res)):
                if new_int(res[i]) >= len(majors) or new_int(res[i]) < 0:
                    await member.send(
                        f'Your response is not a valid answer, expected answers must only include numbers between 0 and {len(majors) - 1}')
                    done = 0
                    break
                res_long.append(majors[new_int(res[i])][0])
                res_short += majors[new_int(res[i])][1] + "/"
            if done == 1:
                await member.send(
                    f'''Your response: {"".join(filter(lambda x: x != "[" and x != "]" and x != "'", str(res_long)))}''')
                return res_short[:-1]
        else:
            await member.send(
                'What department/group do you work in? (please respond with the abbreviation for your depart or group, eg. ECSE, MANE, CATS etc. this will appear in your server nickname, so please try to keep it short)')
            response = await bot.wait_for('message', check=lambda m: m.author == member and isinstance(m.channel, discord.DMChannel))
            if len(response.content) > 10:
                await member.send(
                    'Your response is not a valid answer, expected answers must be less than 10 characters')
                continue
            await member.send(f'Your response: {response.content}')
            return response.content


async def ask_gradyear(member, response_case):
    it = 0
    while it < maxiter:
        it += 1
        if response_case == 2:
            await member.send(
                'If you graduated from RPI what year did you do so? (please respond with a four-digit year eg. 2000 or "N/A" if you did not graduate from RPI)')
        elif response_case == 3:
            await member.send(
                'What year did you graduate from RPI? (please respond with a four-digit year eg. 2000)')
        else:
            await member.send(
                'What is your expected graduation year? (please respond with a four-digit year eg. 2000)')
        response = await bot.wait_for('message', check=lambda m: m.author == member and isinstance(m.channel, discord.DMChannel))
        if response_case == 2 and (response.content.count('n') > 0 or response.content.count('N') > 0) and (response.content.count('a') > 0 or response.content.count('A') > 0):
            await member.send(f'Your response: N/A')
            return ""
        elif len(''.join(filter(str.isdigit, response.content))) == 4:
            res = ''.join(filter(str.isdigit, response.content))
            await member.send(f'Your response: {res}')
            return res
        else:
            await member.send(
                'Your response is not a valid answer, expected answers must be a four-digit number (or N/A for Faculty/Staff)')
            continue


async def ask_eula(member):
    iter7 = 0
    while iter7 < maxiter:
        iter7 += 1
        await member.send(
            'Do you agree to follow all rules laid out in the #rules channel of the RPI Robotics Club server? (Please respond with y/n)')
        response = await bot.wait_for('message', check=lambda m: m.author == member and isinstance(m.channel, discord.DMChannel))
        if len(''.join(filter(lambda x: x == 'y' or x == 'Y', response.content))):
            await member.send(f'Your response: Yes')
            return 'Yes'
        else:
            await member.send(
                "Agreeing to follow the server rules is a requirement for joining the RPI robotics club discord server, failure to agree to our rules will result in not being permitted access to the rest of the server")
            continue


async def ask_email(member, response_case, updating_row=None):
    done = 0
    otp_burn = 1
    message = 0
    otp = 0
    iter1 = 0
    while iter1 < maxiter:
        iter1 += 1
        sub_esc = 0
        if response_case != 3:
            await member.send('What is your RPI email address?')
        else:
            await member.send('What is your email address?')
        response = await bot.wait_for('message', check=lambda m: m.author == member and isinstance(m.channel, discord.DMChannel))
        if response_case != 3 and response.content[-8:] != "@rpi.edu":
            await member.send(
                'Your response is not a valid answer, expected answers must be an email address ending with "@rpi.edu"')
            continue
        elif not (re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$', response.content)):
            await member.send('Your response is not a valid answer, expected answers must be a valid email address')
            continue
        elif not Di.unique_on_col(response.content, 8, ignore_row_index=updating_row):
            await member.send(
                'Your response is not a valid answer, this is a duplicate value with another member\'s data and is therefore not allowed in order to prevent alt accounts.(if you believe this is an error, or you would like to request permission for an alt account, please contact our moderators an they can assist you)')
            continue
        else:
            await member.send(f'Your response: {response.content}')
            await member.send(
                f'you will be sent an email at {response.content} shortly. Please Respond here with the 6-digit code sent in that email. After this, your server verification will be complete!\n(Be sure to check your junk mail as it is likely to be flagged as spam. Additionally, if you need the email to be resent reply "1", and if you need to re-enter your email, reply "2")')
            # Create a SendGrid client
            sg = sendgrid.SendGridAPIClient(api_key=CONFIG.sendgrid_token)
            iter2 = 0
            while iter2 < maxiter:
                iter2 += 1
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
                    iter3 = 0
                    while iter3 < maxiter:
                        iter3 += 1
                        otp_response = await bot.wait_for('message', check=lambda m: m.author == member and isinstance(m.channel, discord.DMChannel))
                        check = new_int(''.join(filter(str.isdigit, otp_response.content)))
                        if check != int(otp) and check != 1 and check != 2:
                            await member.send('The code you sent is not valid, please ensure you typed it correctly and try again. (If you need the email to be resent reply "1". If you need to re-enter your email, reply "2")')
                        elif check == 1:
                            break
                        elif check == 2:
                            sub_esc = 1
                            break
                        else:
                            await member.send("Your Email is now verified and you will be admitted to the server momentarily")
                            return response.content
                else:
                    await mod_report(f"Failed to send email. Status code: {reply.status_code}\n{reply.body}",
                                     mention_mod=True)
                    otp_burn = 0
                    continue
        if done == 1:
            break


async def process_verification(member, reply_channel=None):
    await mod_report("beginning verification for: " + str(member.id))
    # Send a welcome message in the server channel and DM to the new member
    public_welcome = f'Thank you for beginning the verification process, {member.mention}! I will DM you momentarily to get started.'
    private_welcome = 'In order to verify you for access to the server we ask that you please answer the following 7-8 questions. (if you make any mistakes entering your data, you can update it after you have completed verification using the !update command)'

    if reply_channel:
        await reply_channel.send(public_welcome)

    await member.send(private_welcome)

    # Begin asking questions:
    responses = [member.id]

    # Question 1
    responses.append(await ask_fname(member))

    # Question 2
    responses.append(await ask_lname(member))

    # Question 3
    response, response_case = await ask_type(member)
    responses.append(response)

    # Filter out guests
    if response_case != False:

        # Question 4
        responses.append(await ask_rin(member, response_case))

        # Question 5
        responses.append(await ask_major(member, response_case))

        # Question 6
        responses.append(await ask_gradyear(member, response_case))

        # Question 7
        responses.append(await ask_eula(member))

        # Question 8
        responses.append(await ask_email(member, response_case))

        # Add data to csv
        Di.add_data(responses)

        # Updates Nickname
        await nick_set(member)

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

        await mod_report(f"new {mem_type} added to server with nickname {member.display_name}\nresponses: {str(responses)}", mention_mod=priority)


async def process_update(member, alt_updater=False):
    data = Di.get_data(member.id)
    to_update = []
    headers = Di.get_headers()
    data_index = Di.get_data(member.id, index=True)

    message = f"The current data stored for member {member.display_name} is as follows:```"
    for i in range(len(data)-1):
        message += f"{i+1}) {headers[i+1]}: {data[i+1]}\n"
    message += '```Please respond with the number(s) corresponding to the field(s) you wish to update. (if you wish to update multiple fields enter the numbers separated by commas eg. "4" or "2,4,8")'
    if Di.data_validate(member.id) != True:
        message += f"\nAdditionally due to unexpected data found in your records you will be required to update the following fields along with any others that you choose to update.\nRequired fields:{Di.data_validate(member.id)}"
        to_update.extend(Di.data_validate(member.id))

    if alt_updater != False:
        member = alt_updater

    it = 0
    while it < maxiter:
        it += 1
        done = 1
        await member.send(message)
        response = await bot.wait_for('message', check=lambda m: m.author == member and isinstance(m.channel, discord.DMChannel))
        res = ''.join(filter(lambda x: x == ',' or x.isdigit(), response.content))
        res = res.split(',')
        res = [int(i) for i in res]
        if len(res) < 1:
            await member.send(
                f'Your response is not a valid answer, expected answers must include  at least one number between 1 and {len(data)}')
            continue
        for i in range(len(res)):
            if int(res[i]) >= len(data) or new_int(res[i]) <= 0:
                await member.send(
                    f'Your response is not a valid answer, expected answers must only include numbers between 1 and {len(data)}')
                done = 0
                break
            to_update.extend(res)
        if done == 1:
            to_update = list(set(to_update))
            await member.send(
                f'''Your response: {"".join(filter(lambda x: x != "[" and x != "]" and x != "'", str(to_update)))}''')
            break

    if it == maxiter:
        raise ValueError

    if 1 in to_update:
        data[1] = await ask_fname(member)

    if 2 in to_update:
        data[2] = await ask_lname(member)

    if 3 in to_update:
        data[3], response_case = await ask_type(member, allow_guest=False)
    else:
        if data[3] == "Student":
            response_case = 1
        elif data[3] == "Faculty/Staff":
            response_case = 2
        else:
            response_case = 3

    if 4 in to_update:
        data[4] = await ask_rin(member, response_case, updating_row=data_index)

    if 5 in to_update:
        data[5] = await ask_major(member, response_case)

    if 6 in to_update:
        data[6] = await ask_gradyear(member, response_case)

    if 7 in to_update:
        data[7] = await ask_eula(member)

    if 8 in to_update:
        data[8] = await ask_email(member, response_case, updating_row=data_index)

    Di.data_update(data)

    await member.send('''Your update has been processed!''')

    await nick_set(member)

    # notify moderator of new member
    if response_case != 1:
        priority = True
    else:
        priority = False

    mem_type = ['error', "student", "faculty/staff member", "alumnus"][response_case]

    await mod_report(
        f"{member.display_name} updated data\nmember type: {mem_type}\nnew data: {str(data)}\nfields updated: {to_update}",
        mention_mod=priority)


@bot.event
async def on_ready():
    await mod_report(f'Logged in as {bot.user.name}')


@bot.event
async def on_member_join(member):
    # check for correct server
    if member.guild.id == CONFIG.discord_guild_id:
        # public_welcome = f'Welcome to the server, {member.mention}!\nTo gain access to the full server we require you complete a brief verification process, to start the process type !verify and I\'ll send you the next steps.'
        #
        # welcome_channel = member.guild.system_channel
        # if welcome_channel:
        #     await welcome_channel.send(public_welcome)
        # await update_roles(member, rc.case0)
        await member.add_roles(rc.Member);


@bot.event
async def on_member_remove(member):
    # check for correct server
    if member.guild.id == CONFIG.discord_guild_id:
        await mod_report(f"member: {member.nick} \ndeparted with data: {Di.get_data(member.id)}")
        Di.rem_data(member.id)


@bot.command()
async def force_verification(ctx, member: discord.Member):
    # check for correct server
    if ctx.guild.id == CONFIG.discord_guild_id:
        # Check if the command invoker has permission to use the command
        if ctx.author.guild_permissions.administrator:
            await ctx.send(f'Starting verification process for {member.mention}...')
            await process_verification(member)  # Manually trigger the on_member_join event for the specified member
        else:
            await ctx.send('You do not have permission to use this command.')


@bot.command()
async def verify(ctx):
    # check for correct server
    if ctx.guild.id == CONFIG.discord_guild_id:
        if any(role.id == rc.New for role in ctx.author.roles):
            await process_verification(ctx.author, reply_channel=ctx.channel)


@bot.command()
async def remove(ctx, member: discord.Member):
    # check for correct server
    if ctx.guild.id == CONFIG.discord_guild_id:
        # Check if the command invoker has permission to use the command
        if ctx.author.guild_permissions.administrator:
            await update_roles(member, rc.case0, keep_only_specified=True)
            await ctx.send(f"removing member with data: {Di.get_data(member.id)}")
            Di.rem_data(member.id)
        else:
            await ctx.send('You do not have permission to use this command.')


@bot.command()
async def update(ctx):
    # check for correct server
    if ctx.guild.id == CONFIG.discord_guild_id:
        if not any(role.id == rc.New for role in ctx.author.roles):
            await process_update(ctx.author)


bot.run(CONFIG.discord_token)
